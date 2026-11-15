/**
 * Plugin-wide developer/diagnostic toggles. Currently houses the log-level
 * dropdown and the self-update control; future additions belong here when
 * they're orthogonal to any other panel.
 *
 * The update field is the answer to a real constraint: on a Deck in Game Mode
 * there is no terminal, and the installed folder belongs to root — so the only
 * passwordless way to replace it is from inside the loader, which is what this
 * button calls.
 */

import { FC, useState } from "react";
import { PanelSection, PanelSectionRow, DropdownItem, ButtonItem, TextField, Focusable } from "@decky/ui";
import { toaster } from "@decky/api";

import { updatePlugin } from "../../api/backend";

interface AdvancedSectionProps {
  logLevel: string;
  onLogLevelChange: (level: string) => void;
}

export const AdvancedSection: FC<AdvancedSectionProps> = ({ logLevel, onLogLevelChange }) => {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);

  const runUpdate = async () => {
    // An empty field is the ordinary case: the backend installs this project's
    // newest build, so updating needs no pasted link.
    const target = url.trim();
    if (busy) {
      return;
    }
    setBusy(true);
    try {
      const result = await updatePlugin(target);
      toaster.toast({
        // Three outcomes, not two: being current is not a refusal, and a person who
        // pressed Update on an unchanged device should read that as an answer.
        title: result.up_to_date ? "Already up to date" : result.success ? "Updating Arcoon Deck" : "Update refused",
        body: result.message,
      });
    } catch (error) {
      toaster.toast({ title: "Update failed", body: String(error) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <PanelSection title="Advanced">
      <PanelSectionRow>
        <DropdownItem
          label="Log Level"
          description="Controls how much detail is written to plugin logs"
          rgOptions={[
            { data: "error", label: "Error" },
            { data: "warn", label: "Warn" },
            { data: "info", label: "Info" },
            { data: "debug", label: "Debug" },
          ]}
          selectedOption={logLevel}
          onChange={(option) => onLogLevelChange(option.data)}
        />
      </PanelSectionRow>
      <PanelSectionRow>
        <TextField
          label="Update from URL"
          description="Leave empty to install the newest build from this project's repository — paste a zip address to install a different build"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
        />
      </PanelSectionRow>
      <PanelSectionRow>
        <Focusable>
          <ButtonItem
            layout="below"
            disabled={busy}
            onClick={() => {
              void runUpdate();
            }}
          >
            {busy ? "Updating…" : "Update now"}
          </ButtonItem>
        </Focusable>
      </PanelSectionRow>
    </PanelSection>
  );
};
