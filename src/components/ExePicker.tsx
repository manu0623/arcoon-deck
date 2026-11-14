/**
 * ExePicker — the Windows-platform game's executable, and the ones it could be.
 *
 * A RomM Windows entry is played by no emulator: Steam starts the game's own
 * `.exe`, under Proton, and the shortcut's exe is therefore the whole launch. The
 * backend guesses which file that is when the game is downloaded; a game folder
 * can also hold a launcher, an uninstaller and a suite of tools, and nothing in a
 * filename proves which one a person wants to press. This is the manual half.
 *
 * Renders as one row in the ROM File section — the recorded executable, with a
 * trigger that opens the ranked list. The list is fetched on the press rather
 * than on mount: every game page renders this section, and only a Windows install
 * has an answer to fetch.
 *
 * Picking rewrites the install's recorded launch file (backend) and the live
 * shortcut's exe/start dir (frontend — the only side that can write Steam's
 * store). The write rides a prune lease for the same reason the disc picker's
 * does: the removed-game cleanup could retire the shortcut mid-write.
 */

import { FC, useEffect, useState } from "react";
import { Menu, MenuItem, showContextMenu, DialogButton } from "@decky/ui";
import { FaWindows, FaChevronDown } from "react-icons/fa";
import { getLaunchExe, setLaunchExe, logError, logWarn } from "../api/backend";
import { setShortcutTarget } from "../utils/steamShortcuts";
import { getEventTarget } from "../utils/events";
import { detach } from "../utils/detach";
import { showToast } from "../utils/toast";
import {
  capturePruneLeaseAdmission,
  isPruneLeaseCancellation,
  mountPruneLeaseOwner,
  releasePruneLeasesByOwner,
  withPruneLease,
} from "../utils/pruneLease";

interface ExePickerProps {
  appId: number;
  romId: number;
  /** The recorded launch file's name, shown before the first pick. */
  current: string;
}

const EXE_GREY = "#dcdedf";
const EXE_ACCENT = "#59b6ff";

/** The shortest label that still tells two candidates apart. */
function labelFor(path: string): string {
  const parts = path.split("/");
  return parts.length > 1 ? `${parts[parts.length - 1]}  ·  ${parts.slice(0, -1).join("/")}` : path;
}

export const ExePicker: FC<ExePickerProps> = ({ appId, romId, current }) => {
  const leaseOwner = `exe-picker:${appId}`;
  const [selected, setSelected] = useState<string | null>(null);

  const choose = async (path: string): Promise<void> => {
    const admission = capturePruneLeaseAdmission(leaseOwner);
    try {
      const result = await setLaunchExe(romId, path);
      await withPruneLease(
        result.prune_lease_token,
        "Launch exe",
        async (signal) => {
          if (!result.success) {
            showToast(result.message || "Couldn't use that executable");
            return;
          }
          if (signal.aborted) return;
          if (result.exe && result.start_dir != null) {
            setShortcutTarget(appId, result.exe, result.start_dir);
          }
          setSelected(path);
        },
        leaseOwner,
        admission,
      );
    } catch (e) {
      // Leaving the game page cancels the continuation — the pick is already
      // persisted backend-side, so that is teardown rather than a failure.
      if (isPruneLeaseCancellation(e, admission)) {
        logWarn(`ExePicker: launch target continuation was cancelled: ${e}`);
        return;
      }
      logError(`ExePicker: setLaunchExe failed: ${e}`);
      showToast("Couldn't use that executable");
    }
  };

  const openMenu = (e: MouseEvent): void => {
    detach(
      (async () => {
        let selection;
        try {
          selection = await getLaunchExe(romId);
        } catch (err) {
          logError(`ExePicker: getLaunchExe failed: ${err}`);
          showToast("Couldn't read this game's files");
          return;
        }
        if (!selection.windows) return;
        const candidates = selection.candidates ?? [];
        if (candidates.length === 0) {
          // A single-file install owns no folder, so there is exactly one thing it
          // could run — say so rather than opening an empty menu.
          showToast("This game installs as a single executable");
          return;
        }
        const activePath = selected ?? selection.current;
        showContextMenu(
          <Menu label="Launches">
            {candidates.map((candidate) => {
              const active = candidate.path === activePath;
              return (
                <MenuItem key={candidate.path} onClick={() => detach(choose(candidate.path))}>
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "10px",
                      color: active ? EXE_ACCENT : undefined,
                    }}
                  >
                    <FaWindows size={14} />
                    <span>{labelFor(candidate.path)}</span>
                    {active ? <span style={{ marginLeft: "6px", fontWeight: 700 }}>✓</span> : null}
                  </span>
                </MenuItem>
              );
            })}
            {selection.truncated ? <MenuItem disabled>The list was cut to 60 files</MenuItem> : null}
          </Menu>,
          getEventTarget(e),
        );
      })(),
    );
  };

  // The lease owner lives exactly as long as the row: mounted with it, released
  // when the page goes away so nothing holds a lease no continuation can use.
  useEffect(() => {
    mountPruneLeaseOwner(leaseOwner);
    return () => {
      detach(releasePruneLeasesByOwner(leaseOwner));
    };
  }, [leaseOwner]);

  return (
    <div className="romm-panel-info-row">
      <span className="romm-panel-label">Launches</span>
      <span style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: EXE_GREY }}>
        <FaWindows size={14} />
        <span>{labelFor(selected ?? current)}</span>
        <DialogButton className="romm-disc-btn" onClick={openMenu}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
            Change
            <FaChevronDown size={10} color="#cfd3d8" />
          </span>
        </DialogButton>
      </span>
    </div>
  );
};
