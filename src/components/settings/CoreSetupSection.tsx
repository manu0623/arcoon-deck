/**
 * Emulators and cores — the one action that makes a bare device able to launch.
 *
 * The panel can install its own runtime, but until this existed nothing in the UI
 * called the backend that does it: a device with no emulators had a library, a
 * picker, and no way to fetch what launches anything. That is what this section is
 * for, and it is deliberately one button: the reader does not know which platform
 * needs which core, and should not have to.
 *
 * The action is user-triggered rather than automatic on launch, because a launch
 * that waits on a download hangs when the network is down, and a core is a
 * one-time install per platform.
 */

import { FC } from "react";
import { PanelSection, PanelSectionRow, ButtonItem } from "@decky/ui";

export interface CoreSetupSectionProps {
  /** A provisioning run is in flight. The button is dead and says so while it is. */
  busy: boolean;
  /** What the last run did — counts, or the failure it hit. */
  status: string;
  onInstall: () => void;
  /** Which runtime is driving: "standalone" (default), "retrodeck" or "auto" (ADR-0045). */
  runtimeMode: string;
  onRuntimeChange: (mode: string) => void;
}

/** The three runtimes, in the order the choice reads: the app's own first. */
const RUNTIME_CHOICES: ReadonlyArray<{ id: string; label: string }> = [
  { id: "standalone", label: "This app" },
  { id: "retrodeck", label: "RetroDECK" },
  { id: "auto", label: "Follow what's installed" },
];

export const CoreSetupSection: FC<CoreSetupSectionProps> = ({
  busy,
  status,
  onInstall,
  runtimeMode,
  onRuntimeChange,
}) => (
  <PanelSection title="Emulators & Cores">
    <PanelSectionRow>
      <div style={{ fontSize: "11px", color: "#8f98a0", padding: "0 0 6px" }}>
        Runtime — the app installs and launches its own RetroArch, so its saves are the ones it can answer for.
        RetroDECK is a fallback you choose, never a requirement.
      </div>
    </PanelSectionRow>
    {RUNTIME_CHOICES.map(({ id, label }) => (
      <PanelSectionRow key={id}>
        <ButtonItem
          layout="below"
          onClick={() => onRuntimeChange(id)}
          disabled={runtimeMode === id}
        >
          {runtimeMode === id ? `${label} — in use` : label}
        </ButtonItem>
      </PanelSectionRow>
    ))}
    <PanelSectionRow>
      <ButtonItem layout="below" onClick={onInstall} disabled={busy}>
        {busy ? "Installing cores…" : "Install Missing Cores"}
      </ButtonItem>
    </PanelSectionRow>
    <PanelSectionRow>
      <div style={{ fontSize: "11px", color: "#8f98a0", padding: "0 0 6px" }}>
        Downloads the RetroArch runtime and the cores your enabled platforms launch with, then verifies each one.
        Standalone emulators are not covered yet.
      </div>
    </PanelSectionRow>
    {status !== "" && (
      <PanelSectionRow>
        <div style={{ fontSize: "12px", color: "#dcdedf" }}>{status}</div>
      </PanelSectionRow>
    )}
  </PanelSection>
);
