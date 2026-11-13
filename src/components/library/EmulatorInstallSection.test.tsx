/**
 * The platform pane's install action: what it lists, what one press does, and what it says
 * when the backend refuses.
 *
 * The backend is mocked at the module seam — the adapter's own behaviour is pinned in
 * Python — so what is asserted here is the pane's arithmetic: one call per emulator in
 * order, each row reporting its own outcome, and rows with no source named rather than
 * dropped.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, fireEvent, waitFor } from "@testing-library/react";
import { EmulatorInstallSection } from "./EmulatorInstallSection";
import * as backend from "../../api/backend";

vi.mock("../../api/backend", () => ({
  getPlatformEmulators: vi.fn(),
  ensurePlatformEmulator: vi.fn(),
  logWarn: vi.fn(),
}));

const mocked = backend as unknown as {
  getPlatformEmulators: ReturnType<typeof vi.fn>;
  ensurePlatformEmulator: ReturnType<typeof vi.fn>;
  logWarn: ReturnType<typeof vi.fn>;
};

const _psp = { label: "PPSSPP (Standalone)", source: "release" as const, app_id: null, repo: "hrydgard/ppsspp" };
const _dolphin = {
  label: "Dolphin (Standalone)",
  source: "store" as const,
  app_id: "org.DolphinEmu.dolphin-emu",
  repo: null,
};
const _rows = [_psp, _dolphin];

beforeEach(() => {
  vi.clearAllMocks();
});

describe("EmulatorInstallSection", () => {
  it("names the rows with no source instead of hiding them", async () => {
    mocked.getPlatformEmulators.mockResolvedValue({
      system: "switch",
      known: true,
      emulators: [],
      manual: ["Eden (Standalone)"],
    });

    const { findByText } = render(<EmulatorInstallSection slug="switch" />);

    expect(await findByText(/Install by hand/)).toHaveTextContent("Eden (Standalone)");
    expect(mocked.getPlatformEmulators).toHaveBeenCalledWith("switch");
  });

  it("renders nothing on a platform with no standalone emulator at all", async () => {
    mocked.getPlatformEmulators.mockResolvedValue({ system: "gba", known: true, emulators: [], manual: [] });

    const { container, queryByText } = render(<EmulatorInstallSection slug="gba" />);

    await waitFor(() => expect(mocked.getPlatformEmulators).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
    expect(queryByText("Standalone emulators")).not.toBeInTheDocument();
  });

  it("installs each listed emulator in order and reports each outcome", async () => {
    mocked.getPlatformEmulators.mockResolvedValue({ system: "psp", known: true, emulators: _rows, manual: [] });
    mocked.ensurePlatformEmulator
      .mockResolvedValueOnce({ label: _psp.label, ok: true, already_present: false, version: "v1.20.4" })
      .mockResolvedValueOnce({ label: _dolphin.label, ok: true, already_present: true });

    const { findByRole, findByText } = render(<EmulatorInstallSection slug="psp" />);

    fireEvent.click(await findByRole("button", { name: /Install emulators/ }));

    expect(await findByText(/Installed PPSSPP \(Standalone\) v1\.20\.4/)).toBeInTheDocument();
    expect(await findByText(/Dolphin \(Standalone\) is already installed/)).toBeInTheDocument();
    expect(mocked.ensurePlatformEmulator.mock.calls).toEqual([
      ["psp", "PPSSPP (Standalone)"],
      ["psp", "Dolphin (Standalone)"],
    ]);
  });

  it("says why a refused install was refused", async () => {
    mocked.getPlatformEmulators.mockResolvedValue({
      system: "psx",
      known: true,
      emulators: [{ label: "DuckStation (Standalone)", source: "release", app_id: null, repo: "stenzek/duckstation" }],
      manual: [],
    });
    mocked.ensurePlatformEmulator.mockResolvedValue({
      label: "DuckStation (Standalone)",
      ok: false,
      reason: "hash_mismatch",
    });

    const { findByRole, findByText } = render(<EmulatorInstallSection slug="psx" />);

    fireEvent.click(await findByRole("button", { name: /Install emulator/ }));

    expect(await findByText(/did not match the hash/)).toBeInTheDocument();
  });

  it("names the state of the read when it could not be made", async () => {
    mocked.getPlatformEmulators.mockRejectedValue(new Error("net"));

    const { findByText } = render(<EmulatorInstallSection slug="ps3" />);

    expect(await findByText(/Could not read which emulators/)).toBeInTheDocument();
    expect(mocked.logWarn).toHaveBeenCalled();
  });
});
