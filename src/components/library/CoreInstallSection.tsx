/**
 * A platform's libretro cores, and the button that fetches them again.
 *
 * The pane could already say which core launches a platform and install the one a
 * device is missing, but nothing in it could replace a core that is *there*: a
 * `.so` written by an older build that RetroArch refuses to load, or one older
 * than the build bot's nightly. The missing-only sweep skips both by design — it
 * asks the filesystem, and the filesystem says the file exists.
 *
 * Two states, one button, because they are the same action with a different
 * target: cores missing → fetch those; every core present → re-fetch all of them
 * (`force`). The label states which, so a reader never presses "Reinstall" over a
 * platform that was only half installed and gets a full download without knowing.
 *
 * Structure and vocabulary: `docs/architecture/qam-panel.md`, section Library.
 */

import type { FC } from "react";
import { useState } from "react";
import { DialogButton, Spinner } from "@decky/ui";
import { ensurePlatformCores, logWarn } from "../../api/backend";
import type { EmulatorOption, SystemCoreInfo } from "../../types/firmware";
import { FLAT_BUTTON, GREEN, MUTED, Muted, RED, SECONDARY_FONT, SectionTitle } from "../qam/pane";

/** What the run is doing, in the pane's own three-way vocabulary. */
type RunState =
  { kind: "idle" } | { kind: "running" } | { kind: "done"; text: string } | { kind: "failed"; text: string };

/**
 * The refusals a reader can act on, in plain words.
 *
 * The backend's reasons are stable codes because they travel over the wire; these
 * are the sentences. An unknown code is shown as-is rather than folded into a
 * generic "failed", because nothing here knows what it means and inventing a
 * meaning would hide the one fact the answer carried.
 */
const REASON_TEXT: Record<string, string> = {
  no_cores_dir: "there is no cores folder to install into — the runtime is not installed yet",
  not_a_zip: "the download was not the archive the build bot publishes",
  no_core_member: "the archive did not contain this core",
  corrupt_member: "the archive was truncated or corrupt",
  too_small: "the download was too small to be a core",
  not_elf: "the download was not a Linux core",
  unknown_system: "this build has no emulator data for this platform",
  no_libretro: "this platform launches with standalone emulators, not libretro cores",
};

/** ``download_failed: …`` and friends: the detail after the colon is the useful half. */
const reasonText = (reason: string | undefined): string => {
  if (!reason) return "the download did not finish";
  const [code = ""] = reason.split(":", 1);
  const known = REASON_TEXT[code];
  if (known) return known;
  const detail = reason.includes(":") ? reason.slice(reason.indexOf(":") + 1).trim() : reason;
  return detail || "it could not be installed";
};

/** The cores worth fetching, one row per core file — two labels can name one core. */
const coresFor = (core: SystemCoreInfo): EmulatorOption[] => {
  const seen = new Set<string>();
  return core.emulators.filter((option) => {
    if (option.kind !== "libretro" || !option.core_so || seen.has(option.core_so)) return false;
    seen.add(option.core_so);
    return true;
  });
};

export const CoreInstallSection: FC<{ slug: string; core: SystemCoreInfo | null | undefined }> = ({ slug, core }) => {
  const [state, setState] = useState<RunState>({ kind: "idle" });

  // No read, no list, or nothing libretro on it: the standalone section below is
  // the one with something to say, and a title over an empty body would be noise.
  if (!core || !core.emulator_data_available) return null;
  const rows = coresFor(core);
  if (rows.length === 0) return null;

  const installed = rows.filter((row) => row.reason === null).length;
  const missing = rows.length - installed;
  // Missing cores first: fetching only those is the cheap, obvious repair. With
  // every core on disk the same button re-fetches them all.
  const force = missing === 0;
  const label = force
    ? rows.length > 1
      ? "Reinstall cores"
      : "Reinstall core"
    : missing > 1
      ? `Download ${missing} missing cores`
      : "Download the missing core";

  const run = async () => {
    if (state.kind === "running") return;
    setState({ kind: "running" });
    try {
      const result = await ensurePlatformCores(slug, force);
      const landed = result.installed ?? [];
      const failed = result.failed ?? [];
      if (failed.length > 0) {
        const first = failed[0];
        setState({ kind: "failed", text: `${first?.core ?? "a core"}: ${reasonText(first?.reason)}` });
        return;
      }
      if (!result.success) {
        setState({ kind: "failed", text: reasonText(result.reason) });
        return;
      }
      const verb = force ? "Reinstalled" : "Installed";
      const count = landed.length;
      setState({
        kind: "done",
        text: count === 1 ? `${verb} ${landed[0]?.replace(/_libretro$/, "")}.` : `${verb} ${count} cores.`,
      });
    } catch (error: unknown) {
      logWarn(`Installing cores for ${slug} failed: ${String(error)}`);
      setState({ kind: "failed", text: String(error) });
    }
  };

  return (
    <>
      <SectionTitle title="Libretro cores" />
      {rows.map((row) => (
        <div key={row.core_so ?? row.label} style={{ padding: "2px 16px" }}>
          {/* "missing", not "not installed": the pane's own clause says that about the
              EMULATOR, and a second, differently-meant copy of the phrase beside it read
              as the same claim about a different thing. */}
          <span style={{ fontSize: SECONDARY_FONT, color: row.reason === null ? GREEN : MUTED }}>
            {`${row.label} · ${row.reason === null ? "installed" : "missing"}`}
          </span>
        </div>
      ))}
      {state.kind === "done" && (
        <Muted>
          <span style={{ color: GREEN }}>{state.text}</span>
        </Muted>
      )}
      {state.kind === "failed" && (
        <Muted>
          <span style={{ color: RED }}>{state.text}</span>
        </Muted>
      )}
      <div style={{ display: "flex", padding: "6px 16px 2px" }}>
        <DialogButton
          style={FLAT_BUTTON}
          disabled={state.kind === "running"}
          onClick={() => {
            void run();
          }}
        >
          <span style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "13px" }}>
            {state.kind === "running" && <Spinner width={12} height={12} />}
            {state.kind === "running" ? "Downloading…" : label}
          </span>
        </DialogButton>
      </div>
    </>
  );
};
