/**
 * SaveFolderPicker — where a Windows game's saves live, and the folders they could be.
 *
 * A Proton game writes inside its own Wine prefix, so the plugin guesses the save
 * folder from the game's own name (ADR-0074). A guess is allowed to be wrong: the
 * game may keep its profile under a folder named nothing like the title, or under
 * `AppData`. This is the manual half — the detected folder, and a list of the
 * other folders in the same prefix to switch to.
 *
 * Unlike the exe picker, this row has to read on mount: the folder is the answer,
 * not a menu behind a press. Nothing is written to the prefix or to Steam — the
 * pick is the plugin's own record — so there is no prune lease and no shortcut to
 * retarget.
 */

import { FC, useEffect, useState } from "react";
import { Menu, MenuItem, showContextMenu, DialogButton } from "@decky/ui";
import { FaFolderOpen, FaChevronDown, FaCloudDownloadAlt } from "react-icons/fa";
import { getSaveFolder, setSaveFolder, preLaunchSync, logError, logWarn } from "../api/backend";
import type { SaveFolderSelection } from "../api/backend";
import { getEventTarget } from "../utils/events";
import { detach } from "../utils/detach";
import { showToast } from "../utils/toast";

interface SaveFolderPickerProps {
  romId: number;
  /** The game problem's platform slug, so a non-Windows install renders nothing. */
  platformSlug: string;
}

const SAVE_GREY = "#dcdedf";
const SAVE_ACCENT = "#59b6ff";

function isWindowsSlug(slug: string): boolean {
  return slug === "windows" || slug === "win";
}

/** "Documents/NFS Most Wanted  ·  3 files" — the folder, and how much is in it. */
function candidateLabel(path: string, files: number): string {
  return files === 1 ? `${path}  ·  1 file` : `${path}  ·  ${files} files`;
}

export const SaveFolderPicker: FC<SaveFolderPickerProps> = ({ romId, platformSlug }) => {
  const [state, setState] = useState<SaveFolderSelection | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isWindowsSlug(platformSlug)) return;
    let cancelled = false;
    detach(
      (async () => {
        try {
          const result = await getSaveFolder(romId);
          if (!cancelled) setState(result);
        } catch (e) {
          logWarn(`SaveFolderPicker: getSaveFolder failed: ${e}`);
        }
      })(),
    );
    return () => {
      cancelled = true;
    };
  }, [romId, platformSlug]);

  if (!isWindowsSlug(platformSlug) || state === null) return null;

  const choose = async (path: string): Promise<void> => {
    setBusy(true);
    try {
      const result = await setSaveFolder(romId, path);
      if (!result.success) {
        showToast(result.message || "Couldn't use that folder");
        return;
      }
      // Re-read rather than patch: the backend decides what the folder is now.
      setState(await getSaveFolder(romId));
    } catch (e) {
      logError(`SaveFolderPicker: setSaveFolder failed: ${e}`);
      showToast("Couldn't use that folder");
    } finally {
      setBusy(false);
    }
  };

  // The same restore the Play button runs, on demand: a person who cannot tell
  // whether a launch synced can ask for it directly and read the answer. It also
  // covers the folder the game has not created yet, because the save states where
  // it belongs (ADR-0074).
  const restore = async (): Promise<void> => {
    setBusy(true);
    try {
      const result = await preLaunchSync(romId);
      showToast(result.message || (result.success ? "Restored the newest save" : "Couldn't restore the save"));
      // A restore can create the folder, so re-read rather than guess what it did.
      setState(await getSaveFolder(romId));
    } catch (e) {
      logError(`SaveFolderPicker: preLaunchSync failed: ${e}`);
      showToast("Couldn't restore the save");
    } finally {
      setBusy(false);
    }
  };

  const openMenu = (e: MouseEvent): void => {
    const candidates = state.candidates ?? [];
    if (candidates.length === 0) {
      showToast("No save folder has appeared in this game's prefix yet");
      return;
    }
    showContextMenu(
      <Menu label="Saves">
        {state.manual ? (
          <MenuItem onClick={() => detach(choose(""))}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "10px" }}>
              <FaFolderOpen size={14} />
              <span>Detect automatically</span>
            </span>
          </MenuItem>
        ) : null}
        {candidates.map((candidate) => {
          const active = candidate.path === state.folder;
          return (
            <MenuItem key={candidate.path} onClick={() => detach(choose(candidate.path))}>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "10px",
                  color: active ? SAVE_ACCENT : undefined,
                }}
              >
                <FaFolderOpen size={14} />
                <span>{candidateLabel(candidate.path, candidate.files)}</span>
                {active ? <span style={{ marginLeft: "6px", fontWeight: 700 }}>✓</span> : null}
              </span>
            </MenuItem>
          );
        })}
      </Menu>,
      getEventTarget(e),
    );
  };

  return (
    <div className="romm-panel-info-row">
      <span className="romm-panel-label">Saves</span>
      <span style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: SAVE_GREY }}>
        <FaFolderOpen size={14} />
        {state.folder ? (
          <span>
            {state.folder}
            {state.manual ? <span className="romm-panel-muted"> · set by hand</span> : null}
          </span>
        ) : (
          <span className="romm-panel-muted">{state.message || "No save folder yet"}</span>
        )}
        {state.folder ? (
          <DialogButton className="romm-disc-btn" onClick={openMenu} disabled={busy}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
              Change
              <FaChevronDown size={10} color="#cfd3d8" />
            </span>
          </DialogButton>
        ) : null}
        <DialogButton className="romm-disc-btn" onClick={() => detach(restore())} disabled={busy}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
            <FaCloudDownloadAlt size={12} color="#cfd3d8" />
            Restore
          </span>
        </DialogButton>
      </span>
    </div>
  );
};
