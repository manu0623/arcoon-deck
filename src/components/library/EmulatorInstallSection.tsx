/**
 * A platform's standalone emulators, and the button that installs them.
 *
 * The pane could already say which core launches a platform, and on a platform the plugin
 * installs nothing for — Switch, PS3, 3DS, Wii U — nothing it said was actionable. This is
 * that missing action: one press fetches every emulator the inventory names a source for,
 * one row at a time, so the pane reports each build as it lands rather than spinning over
 * a batch.
 *
 * Three things it deliberately does NOT do:
 *
 * - **It names the rows with no source instead of hiding them.** An emulator the plugin
 *   cannot fetch (Eden, whose releases are not reachable from here) is still an emulator
 *   the platform needs; saying "install this one yourself" is the honest answer, and an
 *   empty list would read as "nothing to do".
 * - **It shows the backend's refusal verbatim-ish rather than a generic failure.** "The
 *   download did not match its published hash" and "the release publishes no hash" are
 *   different problems with different fixes, and a surface that folds them into "failed"
 *   hides the one thing it knows.
 * - **It renders nothing on a platform with no standalone row at all.** Most platforms are
 *   libretro-only, and a section title with an empty body on all of them would be noise.
 *
 * Structure and vocabulary: `docs/architecture/qam-panel.md`, section Library.
 */

import type { FC } from "react";
import { useCallback, useEffect, useState } from "react";
import { DialogButton, Spinner } from "@decky/ui";
import { ensurePlatformEmulator, getPlatformEmulators, logWarn, type PlatformEmulatorRow } from "../../api/backend";
import { FLAT_BUTTON, GREEN, MUTED, Muted, RED, SECONDARY_FONT, SectionTitle } from "../qam/pane";

/** What one row is doing, in the pane's own three-way vocabulary. */
type RowState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "installed"; version: string | null }
  | { kind: "present" }
  | { kind: "failed"; reason: string };

/**
 * The refusals a reader can act on, in plain words.
 *
 * The backend's reasons are stable codes because they travel over the wire; these are the
 * sentences. A code with no sentence is shown as-is rather than replaced by "failed":
 * nothing here knows what an unknown reason means, and inventing one would be worse.
 */
const REASON_TEXT: Record<string, string> = {
  no_digest: "the release publishes no hash to check the download against",
  hash_mismatch: "the download did not match the hash its release publishes",
  asset_unresolved: "the release does not attach exactly one Linux build",
  release_unreachable: "the project's release could not be read",
  no_install_path: "the inventory names no place to install it",
  no_source: "the inventory states no source for it",
};

/** ``download_failed: …`` and friends: the detail after the colon is the useful half. */
const reasonText = (reason: string): string => {
  const [code = ""] = reason.split(":", 1);
  const known = REASON_TEXT[code];
  if (known) return known;
  const detail = reason.includes(":") ? reason.slice(reason.indexOf(":") + 1).trim() : reason;
  return detail || "it could not be installed";
};

const sourceText = (row: PlatformEmulatorRow): string =>
  row.source === "store" ? "flatpak store" : row.source === "release" ? "release build" : "no source";

const StatusLine: FC<{ row: PlatformEmulatorRow; state: RowState }> = ({ row, state }) => {
  if (state.kind === "running") {
    return (
      <span
        style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: SECONDARY_FONT, color: MUTED }}
      >
        <Spinner width={10} height={10} />
        {`Installing ${row.label}…`}
      </span>
    );
  }
  if (state.kind === "installed") {
    const suffix = state.version ? ` ${state.version}` : "";
    return <span style={{ fontSize: SECONDARY_FONT, color: GREEN }}>{`Installed ${row.label}${suffix}`}</span>;
  }
  if (state.kind === "present") {
    return <span style={{ fontSize: SECONDARY_FONT, color: GREEN }}>{`${row.label} is already installed`}</span>;
  }
  if (state.kind === "failed") {
    return <span style={{ fontSize: SECONDARY_FONT, color: RED }}>{`${row.label}: ${reasonText(state.reason)}`}</span>;
  }
  // Idle rows state what pressing would fetch, because the two channels differ in ways a
  // reader cares about — a store build updates itself, a release build is a file.
  return <span style={{ fontSize: SECONDARY_FONT, color: MUTED }}>{`${row.label} · ${sourceText(row)}`}</span>;
};

export const EmulatorInstallSection: FC<{ slug: string }> = ({ slug }) => {
  const [rows, setRows] = useState<PlatformEmulatorRow[] | null>(null);
  const [manual, setManual] = useState<string[]>([]);
  const [readFailed, setReadFailed] = useState(false);
  const [rowsState, setRowsState] = useState<Record<string, RowState>>({});
  const [running, setRunning] = useState(false);

  useEffect(() => {
    let live = true;
    setRows(null);
    setManual([]);
    setReadFailed(false);
    setRowsState({});
    // Promised through `.then` so a callable that throws synchronously (no plugin bridge,
    // as in a component test) lands in the same failure branch as one that rejects.
    Promise.resolve()
      .then(() => getPlatformEmulators(slug))
      .then((answer) => {
        if (!live) return;
        setRows(answer.emulators);
        setManual(answer.manual);
      })
      .catch((error: unknown) => {
        if (!live) return;
        logWarn(`Failed to read the installable emulators for ${slug}: ${String(error)}`);
        setReadFailed(true);
      });
    return () => {
      live = false;
    };
  }, [slug]);

  const install = useCallback(async () => {
    if (!rows || rows.length === 0) return;
    setRunning(true);
    // One call per row, in document order, so each line reports its own outcome as it
    // lands. Serial on purpose: two concurrent downloads of a few hundred megabytes each
    // is not a better experience than one at a time.
    for (const row of rows) {
      setRowsState((prev) => ({ ...prev, [row.label]: { kind: "running" } }));
      try {
        const result = await ensurePlatformEmulator(slug, row.label);
        setRowsState((prev) => ({
          ...prev,
          [row.label]: result.ok
            ? result.already_present
              ? { kind: "present" }
              : { kind: "installed", version: result.version ?? null }
            : { kind: "failed", reason: result.reason ?? "it could not be installed" },
        }));
      } catch (error: unknown) {
        logWarn(`Installing ${row.label} for ${slug} failed: ${String(error)}`);
        setRowsState((prev) => ({ ...prev, [row.label]: { kind: "failed", reason: String(error) } }));
      }
    }
    setRunning(false);
  }, [rows, slug]);

  // A platform with no standalone row and nothing manual is a libretro-only platform:
  // there is nothing to say here, and a title over an empty body would say it anyway.
  if (!readFailed && rows !== null && rows.length === 0 && manual.length === 0) return null;

  return (
    <>
      <SectionTitle title="Standalone emulators" />
      {/* Wording kept clear of the pane's other retry sentences: this failure is about a
          supplementary list, not about the platform's own state. */}
      {readFailed && (
        <Muted>Could not read which emulators this platform can install. Reopen the platform to try again.</Muted>
      )}
      {rows?.map((row) => (
        <div key={row.label} style={{ padding: "2px 16px" }}>
          <StatusLine row={row} state={rowsState[row.label] ?? { kind: "idle" }} />
        </div>
      ))}
      {manual.length > 0 && (
        <div style={{ padding: "2px 16px", fontSize: SECONDARY_FONT, color: MUTED }}>
          {`Install by hand — the plugin has no source for ${manual.join(", ")}`}
        </div>
      )}
      {rows !== null && rows.length > 0 && (
        <div style={{ display: "flex", padding: "6px 16px 2px" }}>
          <DialogButton
            style={FLAT_BUTTON}
            disabled={running}
            onClick={() => {
              void install();
            }}
          >
            <span style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "13px" }}>
              {running && <Spinner width={12} height={12} />}
              {rows.length > 1 ? "Install emulators" : "Install emulator"}
            </span>
          </DialogButton>
        </div>
      )}
    </>
  );
};
