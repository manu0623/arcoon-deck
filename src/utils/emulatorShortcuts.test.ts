/**
 * The emulator collection's write half: what one run creates, reuses and repairs.
 *
 * Steam and the backend are both mocked at their module seams, so what is pinned
 * here is the decision table — a bound tile that is still live is left alone, a
 * bound tile Steam lost is created again, an unbound row is created once, and the
 * collection ends up holding exactly the tiles that exist.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import * as backend from "../api/backend";
import * as collections from "./collections";
import * as steamShortcuts from "./steamShortcuts";
import { syncEmulatorShortcuts } from "./emulatorShortcuts";

vi.mock("../api/backend", () => ({
  getEmulatorShortcuts: vi.fn(),
  bindEmulatorShortcut: vi.fn(),
  forgetEmulatorShortcut: vi.fn(),
  getEmulatorArtwork: vi.fn(),
  saveShortcutIcon: vi.fn(),
  logInfo: vi.fn(),
  logWarn: vi.fn(),
  logError: vi.fn(),
}));
vi.mock("./collections", () => ({ createOrUpdateEmulatorCollection: vi.fn() }));
vi.mock("./steamShortcuts", () => ({ addShortcut: vi.fn() }));

const row = (key: string, appId: number | null) => ({
  key,
  name: key.toUpperCase(),
  exe: `/apps/${key}.AppImage`,
  start_dir: "/apps",
  launch_options: "",
  search_term: key.toUpperCase(),
  version: null,
  app_id: appId,
});

const mocked = backend as unknown as Record<keyof typeof backend, ReturnType<typeof vi.fn>>;

function liveStore(appIds: number[]): void {
  vi.stubGlobal("collectionStore", { deckDesktopApps: { apps: new Map(appIds.map((id) => [id, {}])) } });
}

beforeEach(() => {
  vi.resetAllMocks();
  vi.stubGlobal("SteamClient", {
    Apps: { SetCustomArtworkForApp: vi.fn().mockResolvedValue(undefined), SetShortcutIcon: vi.fn() },
  });
  vi.mocked(backend.getEmulatorArtwork).mockResolvedValue({ base64: null, no_api_key: true });
  vi.mocked(backend.bindEmulatorShortcut).mockResolvedValue({ success: true });
  vi.mocked(backend.forgetEmulatorShortcut).mockResolvedValue({ success: true, forgotten: true });
});

describe("syncEmulatorShortcuts", () => {
  it("creates a tile for an unbound emulator and puts it in the collection", async () => {
    liveStore([]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", null)],
    });
    vi.mocked(steamShortcuts.addShortcut).mockResolvedValue(5000);

    const outcome = await syncEmulatorShortcuts();

    expect(vi.mocked(steamShortcuts.addShortcut)).toHaveBeenCalledWith({
      name: "PPSSPP@NATIVE",
      exe: "/apps/ppsspp@native.AppImage",
      start_dir: "/apps",
      launch_options: "",
    });
    expect(mocked.bindEmulatorShortcut).toHaveBeenCalledWith("ppsspp@native", 5000);
    expect(vi.mocked(collections.createOrUpdateEmulatorCollection)).toHaveBeenCalledWith("Emulators", [5000]);
    expect(outcome).toMatchObject({ added: 1, existing: 0, total: 1 });
  });

  it("leaves a live binding alone and creates nothing", async () => {
    liveStore([5000]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", 5000)],
    });
    vi.mocked(backend.getEmulatorArtwork).mockResolvedValue({ base64: null, no_api_key: false, present: true });

    const outcome = await syncEmulatorShortcuts();

    expect(vi.mocked(steamShortcuts.addShortcut)).not.toHaveBeenCalled();
    expect(mocked.getEmulatorArtwork).toHaveBeenCalledTimes(4);
    expect(vi.mocked(SteamClient.Apps.SetCustomArtworkForApp)).not.toHaveBeenCalled();
    expect(mocked.bindEmulatorShortcut).not.toHaveBeenCalled();
    expect(vi.mocked(collections.createOrUpdateEmulatorCollection)).toHaveBeenCalledWith("Emulators", [5000]);
    expect(outcome).toMatchObject({ added: 0, existing: 1, total: 1 });
  });

  it("recreates a bound tile Steam no longer has, and clears the stale binding", async () => {
    liveStore([9999]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", 5000)],
    });
    vi.mocked(steamShortcuts.addShortcut).mockResolvedValue(5001);

    await syncEmulatorShortcuts();

    expect(mocked.forgetEmulatorShortcut).toHaveBeenCalledWith("ppsspp@native");
    expect(vi.mocked(steamShortcuts.addShortcut)).toHaveBeenCalledTimes(1);
    expect(mocked.bindEmulatorShortcut).toHaveBeenCalledWith("ppsspp@native", 5001);
  });

  it("trusts the bindings while Steam's store is still empty", async () => {
    // A plugin mount can run before Steam populates its shortcut map; treating that
    // as "everything is gone" would add a duplicate tile per emulator on every boot.
    liveStore([]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", 5000)],
    });
    vi.mocked(backend.getEmulatorArtwork).mockResolvedValue({ base64: null, no_api_key: false, present: true });

    const outcome = await syncEmulatorShortcuts();

    expect(vi.mocked(steamShortcuts.addShortcut)).not.toHaveBeenCalled();
    expect(mocked.forgetEmulatorShortcut).not.toHaveBeenCalled();
    expect(outcome.existing).toBe(1);
  });

  it("applies the four art assets to a new tile and counts them", async () => {
    liveStore([]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", null)],
    });
    vi.mocked(steamShortcuts.addShortcut).mockResolvedValue(5000);
    vi.mocked(backend.getEmulatorArtwork).mockResolvedValue({ base64: "AA==", no_api_key: false });
    vi.mocked(backend.saveShortcutIcon).mockResolvedValue({ success: true, icon_path: "/grid/5000_icon.png" });

    const outcome = await syncEmulatorShortcuts();

    expect(mocked.getEmulatorArtwork).toHaveBeenCalledTimes(4);
    expect(vi.mocked(SteamClient.Apps.SetCustomArtworkForApp)).toHaveBeenCalledTimes(3);
    expect(vi.mocked(SteamClient.Apps.SetShortcutIcon)).toHaveBeenCalledWith(5000, "/grid/5000_icon.png");
    expect(outcome.art).toBe(4);
  });

  it("dresses an existing tile that has no art yet", async () => {
    // The bug this covers: art was fetched only when the shortcut was created, so the 13
    // tiles a device already had kept Steam's default picture for the life of the install.
    liveStore([5000]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", 5000)],
    });
    vi.mocked(backend.getEmulatorArtwork).mockResolvedValue({ base64: "AA==", no_api_key: false });
    vi.mocked(backend.saveShortcutIcon).mockResolvedValue({ success: true, icon_path: "/grid/5000_icon.png" });

    const outcome = await syncEmulatorShortcuts();

    expect(vi.mocked(steamShortcuts.addShortcut)).not.toHaveBeenCalled();
    expect(mocked.getEmulatorArtwork).toHaveBeenCalledWith("ppsspp@native", 1);
    expect(vi.mocked(SteamClient.Apps.SetCustomArtworkForApp)).toHaveBeenCalledTimes(3);
    expect(vi.mocked(SteamClient.Apps.SetShortcutIcon)).toHaveBeenCalledWith(5000, "/grid/5000_icon.png");
    expect(outcome.art).toBe(4);
  });

  it("writes no collection when there is nothing to put in it", async () => {
    liveStore([]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({ collection: "Emulators", emulators: [] });

    const outcome = await syncEmulatorShortcuts();

    expect(vi.mocked(collections.createOrUpdateEmulatorCollection)).not.toHaveBeenCalled();
    expect(outcome).toMatchObject({ added: 0, existing: 0, total: 0 });
  });

  it("skips a row whose shortcut Steam refuses to create", async () => {
    liveStore([]);
    vi.mocked(backend.getEmulatorShortcuts).mockResolvedValue({
      collection: "Emulators",
      emulators: [row("ppsspp@native", null), row("dolphin@flatpak", null)],
    });
    vi.mocked(steamShortcuts.addShortcut).mockResolvedValueOnce(null).mockResolvedValueOnce(5002);

    const outcome = await syncEmulatorShortcuts();

    expect(mocked.bindEmulatorShortcut).toHaveBeenCalledTimes(1);
    expect(vi.mocked(collections.createOrUpdateEmulatorCollection)).toHaveBeenCalledWith("Emulators", [5002]);
    expect(outcome).toMatchObject({ added: 1, total: 1 });
  });
});
