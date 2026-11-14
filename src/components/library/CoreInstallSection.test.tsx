/**
 * The platform pane's core action: which button a platform gets, what one press
 * asks the backend for, and what it says when the download is refused.
 *
 * The backend is mocked at the module seam — the installer's own checks are
 * pinned in Python — so what is asserted here is the pane's arithmetic: missing
 * cores mean "fetch those", a full set means "re-fetch them all" (`force`), and
 * a refusal is reported in words rather than as a success.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, waitFor } from "@testing-library/react";
import { CoreInstallSection } from "./CoreInstallSection";
import * as backend from "../../api/backend";
import type { EmulatorOption, SystemCoreInfo } from "../../types/firmware";

vi.mock("../../api/backend", () => ({
  ensurePlatformCores: vi.fn(),
  logWarn: vi.fn(),
}));

const mocked = backend as unknown as {
  ensurePlatformCores: ReturnType<typeof vi.fn>;
  logWarn: ReturnType<typeof vi.fn>;
};

function option(label: string, core_so: string, reason: string | null): EmulatorOption {
  return {
    label,
    kind: "libretro",
    core_so,
    emulator: core_so,
    is_default: reason === null,
    bakeable: reason === null,
    reason,
  };
}

function coreInfo(emulators: EmulatorOption[], over: Partial<SystemCoreInfo> = {}): SystemCoreInfo {
  return { emulators, emulator_data_available: true, active_core_label: emulators[0]?.label ?? null, ...over };
}

const _mgba = option("mGBA", "mgba_libretro", null);
const _vbaNextMissing = option("VBA Next", "vba_next_libretro", "not_installed");

beforeEach(() => {
  vi.clearAllMocks();
});

describe("CoreInstallSection", () => {
  it("lists the platform's cores and offers the missing ones", () => {
    const { getByText, getByRole } = render(
      <CoreInstallSection slug="gba" core={coreInfo([_mgba, _vbaNextMissing])} />,
    );

    expect(getByText("mGBA · installed")).toBeInTheDocument();
    expect(getByText("VBA Next · missing")).toBeInTheDocument();
    expect(getByRole("button", { name: /Download the missing core/ })).toBeInTheDocument();
  });

  it("downloads only the missing cores unless every core is present", async () => {
    mocked.ensurePlatformCores.mockResolvedValue({ success: true, installed: ["vba_next_libretro"], failed: [] });
    const { getByRole, findByText } = render(
      <CoreInstallSection slug="gba" core={coreInfo([_mgba, _vbaNextMissing])} />,
    );

    fireEvent.click(getByRole("button", { name: /Download the missing core/ }));

    expect(await findByText("Installed vba_next.")).toBeInTheDocument();
    expect(mocked.ensurePlatformCores).toHaveBeenCalledWith("gba", false);
  });

  it("re-fetches a core that is already on disk", async () => {
    // The state the whole section exists for: the file is there, and the sweep in
    // Settings will never touch it again.
    mocked.ensurePlatformCores.mockResolvedValue({ success: true, installed: ["mgba_libretro"], failed: [] });
    const { getByRole, findByText } = render(<CoreInstallSection slug="gba" core={coreInfo([_mgba])} />);

    fireEvent.click(getByRole("button", { name: /Reinstall core/ }));

    expect(await findByText("Reinstalled mgba.")).toBeInTheDocument();
    expect(mocked.ensurePlatformCores).toHaveBeenCalledWith("gba", true);
  });

  it("reports a refused download in words instead of claiming success", async () => {
    mocked.ensurePlatformCores.mockResolvedValue({
      success: false,
      installed: ["mgba_libretro"],
      failed: [{ core: "vba_next_libretro", reason: "corrupt_member" }],
    });
    const { getByRole, findByText } = render(
      <CoreInstallSection slug="gba" core={coreInfo([_mgba, _vbaNextMissing])} />,
    );

    fireEvent.click(getByRole("button", { name: /Download the missing core/ }));

    expect(await findByText(/vba_next_libretro: the archive was truncated or corrupt/)).toBeInTheDocument();
  });

  it("says nothing on a platform whose emulators are all standalone", () => {
    const standalone: EmulatorOption = {
      label: "PPSSPP (Standalone)",
      kind: "standalone",
      core_so: null,
      emulator: "PPSSPP",
      is_default: true,
      bakeable: true,
      reason: null,
    };
    const { container } = render(<CoreInstallSection slug="psp" core={coreInfo([standalone])} />);

    expect(container).toBeEmptyDOMElement();
  });

  it("holds the button disabled while a download is in flight", async () => {
    let finish!: (result: unknown) => void;
    mocked.ensurePlatformCores.mockReturnValue(
      new Promise((resolve) => {
        finish = resolve;
      }),
    );
    const { getByRole } = render(<CoreInstallSection slug="gba" core={coreInfo([_mgba])} />);

    fireEvent.click(getByRole("button", { name: /Reinstall core/ }));

    expect(getByRole("button", { name: /Downloading…/ })).toBeDisabled();
    finish({ success: true, installed: ["mgba_libretro"], failed: [] });
    await waitFor(() => expect(getByRole("button", { name: /Reinstall core/ })).toBeEnabled());
  });
});
