import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { SaveFolderPicker } from "./SaveFolderPicker";
import { getSaveFolder, preLaunchSync, setSaveFolder } from "../api/backend";
import { showToast } from "../utils/toast";
import type { SaveFolderSelection } from "../api/backend";

vi.mock("../api/backend", () => ({
  getSaveFolder: vi.fn(),
  setSaveFolder: vi.fn(),
  preLaunchSync: vi.fn(),
  logError: vi.fn(),
  logWarn: vi.fn(),
}));

vi.mock("../utils/toast", () => ({ showToast: vi.fn() }));

const FOLDER_SELECTED: SaveFolderSelection = {
  windows: true,
  prefix: true,
  folder: "Documents/NFS Most Wanted",
  manual: false,
  candidates: [{ path: "Documents/NFS Most Wanted", files: 2, modified_at: 1 }],
  message: null,
};

const NO_FOLDER_YET: SaveFolderSelection = {
  windows: true,
  prefix: true,
  folder: null,
  manual: false,
  candidates: [],
  message: "No folder in this game's prefix looks like a save yet.",
};

const restoreButton = () => screen.getByRole("button", { name: /Restore/ });

describe("SaveFolderPicker", () => {
  beforeEach(() => {
    vi.mocked(getSaveFolder).mockReset();
    vi.mocked(setSaveFolder).mockReset();
    vi.mocked(preLaunchSync).mockReset();
    vi.mocked(showToast).mockClear();
  });

  it("renders nothing for a game that is not a Windows install", async () => {
    vi.mocked(getSaveFolder).mockResolvedValue(FOLDER_SELECTED);

    const { container } = render(<SaveFolderPicker romId={7159} platformSlug="snes" />);

    await waitFor(() => expect(getSaveFolder).not.toHaveBeenCalled());
    expect(container.textContent).toBe("");
  });

  it("shows the detected folder and offers the restore", async () => {
    vi.mocked(getSaveFolder).mockResolvedValue(FOLDER_SELECTED);

    render(<SaveFolderPicker romId={7159} platformSlug="win" />);

    await waitFor(() => expect(screen.getByText("Documents/NFS Most Wanted")).toBeInTheDocument());
    expect(restoreButton()).toBeInTheDocument();
  });

  it("restores on demand and reports what happened", async () => {
    const user = userEvent.setup();
    vi.mocked(getSaveFolder).mockResolvedValue(FOLDER_SELECTED);
    vi.mocked(preLaunchSync).mockResolvedValue({ success: true, message: "Restored 7159 [2026-11-15].zip" });

    render(<SaveFolderPicker romId={7159} platformSlug="win" />);
    await waitFor(() => expect(restoreButton()).toBeInTheDocument());

    await user.click(restoreButton());

    await waitFor(() => expect(preLaunchSync).toHaveBeenCalledWith(7159));
    expect(showToast).toHaveBeenCalledWith("Restored 7159 [2026-11-15].zip");
    // The row re-reads, because a restore can create the folder it now shows.
    expect(vi.mocked(getSaveFolder).mock.calls.length).toBeGreaterThan(1);
  });

  it("offers the restore even when no folder has appeared yet", async () => {
    const user = userEvent.setup();
    vi.mocked(getSaveFolder).mockResolvedValue(NO_FOLDER_YET);
    vi.mocked(preLaunchSync).mockResolvedValue({ success: true, message: "Restored 7159 [2026-11-15].zip" });

    render(<SaveFolderPicker romId={7159} platformSlug="win" />);
    await waitFor(() =>
      expect(screen.getByText("No folder in this game's prefix looks like a save yet.")).toBeInTheDocument(),
    );

    await user.click(restoreButton());

    await waitFor(() => expect(preLaunchSync).toHaveBeenCalledWith(7159));
  });

  it("reports a refused restore instead of pretending it worked", async () => {
    const user = userEvent.setup();
    vi.mocked(getSaveFolder).mockResolvedValue(FOLDER_SELECTED);
    vi.mocked(preLaunchSync).mockResolvedValue({
      success: false,
      message: "The save records a folder we cannot follow",
    });

    render(<SaveFolderPicker romId={7159} platformSlug="win" />);
    await waitFor(() => expect(restoreButton()).toBeInTheDocument());

    await user.click(restoreButton());

    await waitFor(() => expect(showToast).toHaveBeenCalledWith("The save records a folder we cannot follow"));
  });
});
