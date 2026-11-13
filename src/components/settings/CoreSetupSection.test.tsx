/**
 * The Emulators & Cores section: the one button that makes a bare device able to
 * launch, and the line that reports what its last run did.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CoreSetupSection } from "./CoreSetupSection";

describe("CoreSetupSection", () => {
  it("offers the install action", () => {
    const onInstall = vi.fn();
    render(<CoreSetupSection busy={false} status="" onInstall={onInstall} />);

    fireEvent.click(screen.getByRole("button", { name: "Install Missing Cores" }));

    expect(onInstall).toHaveBeenCalledTimes(1);
  });

  it("says what it is doing while a run is in flight, and refuses a second press", () => {
    const onInstall = vi.fn();
    render(<CoreSetupSection busy status="" onInstall={onInstall} />);

    const button = screen.getByRole("button", { name: "Installing cores…" });
    fireEvent.click(button);

    expect(button).toBeDisabled();
    expect(onInstall).not.toHaveBeenCalled();
  });

  it("reports the run's result under the button", () => {
    render(<CoreSetupSection busy={false} status="Installed 2 cores." onInstall={vi.fn()} />);

    expect(screen.getByText("Installed 2 cores.")).toBeInTheDocument();
  });

  it("says nothing extra before a run has happened", () => {
    const { container } = render(<CoreSetupSection busy={false} status="" onInstall={vi.fn()} />);

    // The explainer is always there; a status line with no run behind it is not.
    expect(screen.queryByText(/Installed|failed|already installed/)).not.toBeInTheDocument();
    expect(container).toBeDefined();
  });
});
