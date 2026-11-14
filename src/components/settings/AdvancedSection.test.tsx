import { describe, it, expect, vi, beforeEach } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createElement } from "react";
import { toaster } from "@decky/api";
import { updatePlugin } from "../../api/backend";
import { AdvancedSection } from "./AdvancedSection";

vi.mock("../../api/backend", () => ({ updatePlugin: vi.fn() }));

// DropdownItem isn't in the global @decky/ui stub. Capture rgOptions +
// selectedOption + onChange so we can drive the onChange callback and assert
// the wiring without rendering a real Steam Dropdown.
interface DropdownOption {
  data: unknown;
  label: string;
}
interface DropdownItemProps {
  label?: string;
  rgOptions?: DropdownOption[];
  selectedOption?: unknown;
  onChange?: (option: DropdownOption) => void;
}
const captured: { items: DropdownItemProps[] } = { items: [] };

// A local re-mock replaces the whole module, so every component this section
// renders is restated here — not just the dropdown the capture needs.
vi.mock("@decky/ui", () => {
  type AnyProps = Record<string, unknown> & { children?: unknown };
  const passthrough = (tag: string) => (p: AnyProps) => createElement(tag, {}, p.children as never);
  return {
    PanelSection: passthrough("section"),
    PanelSectionRow: passthrough("div"),
    Focusable: passthrough("div"),
    DropdownItem: (p: DropdownItemProps) => {
      captured.items.push(p);
      return createElement("div", { "data-testid": "dropdown" }, p.label as never);
    },
    // Mirrors the global stub: an input whose value the component controls.
    TextField: (p: AnyProps & { value?: string; onChange?: (e: unknown) => void }) =>
      createElement("input", {
        "data-testid": "text-field",
        value: p.value ?? "",
        onChange: (e: unknown) => p.onChange?.(e),
      }),
    // Mirrors the global stub: a real <button>, `disabled` forwarded so a test
    // cannot click an item the component deliberately disabled.
    ButtonItem: (p: AnyProps & { onClick?: () => void; disabled?: boolean }) =>
      createElement(
        "div",
        null,
        createElement("button", { onClick: p.onClick, disabled: p.disabled }, p.children as never),
      ),
  };
});

const updateButton = () => screen.getByRole("button", { name: /Update now|Updating…/ });
const urlField = () => screen.getByTestId("text-field");

describe("AdvancedSection", () => {
  beforeEach(() => {
    captured.items = [];
    vi.mocked(updatePlugin).mockReset();
    vi.mocked(toaster.toast).mockClear();
  });

  it("renders the log-level dropdown with the four canonical options", () => {
    render(<AdvancedSection logLevel="info" onLogLevelChange={vi.fn()} />);
    expect(captured.items).toHaveLength(1);
    const item = captured.items[0];
    expect(item?.label).toBe("Log Level");
    expect(item?.rgOptions?.map((o) => o.data)).toEqual(["error", "warn", "info", "debug"]);
  });

  it("forwards the current logLevel as selectedOption", () => {
    render(<AdvancedSection logLevel="debug" onLogLevelChange={vi.fn()} />);
    expect(captured.items[0]?.selectedOption).toBe("debug");
  });

  it("dispatches onLogLevelChange with option.data when the dropdown fires", () => {
    const onChange = vi.fn();
    render(<AdvancedSection logLevel="info" onLogLevelChange={onChange} />);
    captured.items[0]?.onChange?.({ data: "warn", label: "Warn" });
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith("warn");
  });

  it("passes string values straight through (no transformation)", () => {
    const onChange = vi.fn();
    render(<AdvancedSection logLevel="error" onLogLevelChange={onChange} />);
    captured.items[0]?.onChange?.({ data: "error", label: "Error" });
    expect(onChange).toHaveBeenCalledWith("error");
  });

  // ----------------------------------------------------------------
  // The update control — the section's other setting
  // ----------------------------------------------------------------

  it("keeps Update now disabled until the field holds a real URL", async () => {
    const user = userEvent.setup();
    render(<AdvancedSection logLevel="info" onLogLevelChange={vi.fn()} />);

    expect(updateButton()).toBeDisabled();

    await user.type(urlField(), "   ");
    expect(updateButton()).toBeDisabled();

    await user.type(urlField(), "https://example.test/arcoon.zip");
    expect(updateButton()).toBeEnabled();
  });

  it("installs the zip at the trimmed URL and reports success", async () => {
    const user = userEvent.setup();
    vi.mocked(updatePlugin).mockResolvedValue({ success: true, version: "0.48.43", message: "Installed 0.48.43" });
    render(<AdvancedSection logLevel="info" onLogLevelChange={vi.fn()} />);

    await user.type(urlField(), "  https://example.test/arcoon.zip  ");
    await user.click(updateButton());

    await waitFor(() => expect(updatePlugin).toHaveBeenCalledWith("https://example.test/arcoon.zip"));
    expect(toaster.toast).toHaveBeenCalledWith({ title: "Updating Arcoon Deck", body: "Installed 0.48.43" });
  });

  it("says an update was refused instead of claiming it started", async () => {
    const user = userEvent.setup();
    vi.mocked(updatePlugin).mockResolvedValue({ success: false, message: "Not a plugin zip" });
    render(<AdvancedSection logLevel="info" onLogLevelChange={vi.fn()} />);

    await user.type(urlField(), "https://example.test/notes.txt");
    await user.click(updateButton());

    await waitFor(() =>
      expect(toaster.toast).toHaveBeenCalledWith({ title: "Update refused", body: "Not a plugin zip" }),
    );
  });

  it("reports a thrown install as a failure", async () => {
    const user = userEvent.setup();
    vi.mocked(updatePlugin).mockRejectedValue(new Error("backend exploded"));
    render(<AdvancedSection logLevel="info" onLogLevelChange={vi.fn()} />);

    await user.type(urlField(), "https://example.test/arcoon.zip");
    await user.click(updateButton());

    await waitFor(() =>
      expect(toaster.toast).toHaveBeenCalledWith({ title: "Update failed", body: "Error: backend exploded" }),
    );
  });

  it("holds the button disabled while an install is in flight", async () => {
    const user = userEvent.setup();
    let finish!: (result: { success: boolean; message: string }) => void;
    vi.mocked(updatePlugin).mockReturnValue(
      new Promise((resolve) => {
        finish = resolve;
      }),
    );
    render(<AdvancedSection logLevel="info" onLogLevelChange={vi.fn()} />);

    await user.type(urlField(), "https://example.test/arcoon.zip");
    await user.click(updateButton());

    expect(updateButton()).toBeDisabled();
    expect(updateButton()).toHaveTextContent("Updating…");

    await act(async () => {
      finish({ success: true, message: "Installed" });
    });
    await waitFor(() => expect(updateButton()).toBeEnabled());
  });
});
