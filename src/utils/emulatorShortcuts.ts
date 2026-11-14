/**
 * The emulator collection: one Steam tile per installed emulator.
 *
 * The library's tiles all open a game. Nothing opens an emulator, so the only way
 * to look at one's settings — a controller binding, a BIOS path, whether a build
 * runs at all — was to launch a ROM and back out of it. This creates the missing
 * tile per emulator, gathers them into one collection, and dresses them with
 * SteamGridDB art where SGDB has art to give.
 *
 * Three decisions worth keeping:
 *
 * - **The backend owns the list, Steam owns the writes.** What is installed is a
 *   filesystem question the plugin answers (`get_emulator_shortcuts`); creating a
 *   shortcut or a collection is only possible from inside Steam, so it happens
 *   here. That is also why the binding map lives in the backend's settings: the
 *   run that finds an existing tile must be told so by the backend, not by a scan
 *   of Steam's shortcut store, which costs ~2s per shortcut on a full library.
 * - **A stale binding is repaired, not trusted.** The backend's app id is checked
 *   against Steam's live store; a binding Steam no longer has is forgotten and the
 *   row is created again. The map is a hint, the store is the truth.
 * - **Art is best-effort and never blocks the tile.** No SGDB key, no name match,
 *   a failed download — all just mean the default tile. The shortcut is the
 *   feature; the picture makes it look like it belongs.
 */

import {
  bindEmulatorShortcut,
  forgetEmulatorShortcut,
  getEmulatorArtwork,
  getEmulatorShortcuts,
  logError,
  logInfo,
  logWarn,
  saveShortcutCover,
  saveShortcutIcon,
  type EmulatorShortcutRow,
} from "../api/backend";
import { createOrUpdateEmulatorCollection } from "./collections";
import { addShortcut } from "./steamShortcuts";

/** What one run did, in the terms a status line reads. */
export interface EmulatorCollectionOutcome {
  collection: string;
  added: number;
  existing: number;
  art: number;
  total: number;
}

/** Steam's live non-Steam shortcut app ids, or `null` when it cannot be read. */
function liveShortcutAppIds(): Set<number> | null {
  if (typeof collectionStore === "undefined") return null;
  try {
    // A getter that throws here would escape into whatever render asked for it, so the
    // store is read defensively: no store, no live set, and staleness is simply not judged.
    const apps = collectionStore.deckDesktopApps?.apps;
    return apps ? new Set(apps.keys()) : null;
  } catch (e) {
    logWarn(`Emulator collection: Steam's shortcut store could not be read: ${e}`);
    return null;
  }
}

/**
 * Apply one SGDB asset. Hero, logo and wide grid go through Steam's custom-art
 * call; the icon is a file the backend writes and Steam is pointed at, because an
 * icon needs a path in the grid folder rather than bytes. The portrait cover (5)
 * is a bare grid file too — `{app_id}p.png` is the tile the library grid and a
 * collection show, and Steam reads it from the grid directory without being told.
 */
async function applyAsset(appId: number, key: string, base64: string | null, assetType: number): Promise<boolean> {
  if (!base64) return false;
  try {
    if (assetType === 5) {
      const saved = await saveShortcutCover(appId, base64);
      return saved.success;
    }
    if (assetType === 4) {
      const saved = await saveShortcutIcon(appId, base64);
      if (!saved.success || !saved.icon_path) return false;
      SteamClient.Apps.SetShortcutIcon(appId, saved.icon_path);
      return true;
    }
    await SteamClient.Apps.SetCustomArtworkForApp(appId, base64, "png", assetType);
    return true;
  } catch (e) {
    logWarn(`Emulator artwork: applying asset ${assetType} to ${key} failed: ${e}`);
    return false;
  }
}

/** Fetch and apply all four asset types for one emulator. Returns how many landed. */
async function applyEmulatorArtwork(row: EmulatorShortcutRow, appId: number): Promise<number> {
  const answers = await Promise.all(
    [1, 2, 3, 4, 5].map((assetType) =>
      getEmulatorArtwork(row.key, assetType).catch(() => ({ base64: null, no_api_key: false })),
    ),
  );
  if (answers.some((answer) => answer.no_api_key)) {
    logInfo("Emulator artwork: no SteamGridDB key configured, leaving the default tiles");
    return 0;
  }

  let applied = 0;
  for (const [index, answer] of answers.entries()) {
    if (await applyAsset(appId, row.key, answer.base64, index + 1)) applied++;
  }
  return applied;
}

/**
 * Make Steam's emulator collection match what is installed.
 *
 * Serial across rows on purpose: each row is a shortcut creation plus (for a new
 * tile) up to four art downloads, and doing them one at a time keeps the status
 * line honest and the renderer's memory flat on a Deck.
 */
export async function syncEmulatorShortcuts(): Promise<EmulatorCollectionOutcome> {
  const catalogue = await getEmulatorShortcuts();
  // An empty store is not evidence that every binding is stale: at a plugin mount
  // Steam may simply not have populated its shortcut map yet, and treating that as
  // "all gone" would create a second tile per emulator on every boot. Only a store
  // with something in it is worth checking bindings against.
  const live = liveShortcutAppIds();
  const store = live !== null && live.size > 0 ? live : null;
  const appIds: number[] = [];
  let added = 0;
  let existing = 0;
  let art = 0;

  for (const row of catalogue.emulators) {
    let appId = row.app_id;
    if (appId !== null && store !== null && !store.has(appId)) {
      logWarn(`Emulator collection: ${row.name}'s shortcut (${appId}) is gone; creating it again`);
      try {
        await forgetEmulatorShortcut(row.key);
      } catch (e) {
        logWarn(`Emulator collection: could not clear the stale binding for ${row.key}: ${e}`);
      }
      appId = null;
    }

    if (appId === null) {
      const created = await addShortcut({
        name: row.name,
        exe: row.exe,
        start_dir: row.start_dir,
        launch_options: row.launch_options,
      });
      if (created === null) {
        logError(`Emulator collection: could not create a shortcut for ${row.name}`);
        continue;
      }
      appId = created;
      added++;
      try {
        await bindEmulatorShortcut(row.key, created);
      } catch (e) {
        logWarn(`Emulator collection: could not bind ${row.key} to ${created}: ${e}`);
      }
    } else {
      existing++;
    }
    // Art is applied to a tile that LACKS it, not only to one this run created: a tile
    // bound before the art existed — or before a SteamGridDB key was set — would
    // otherwise wear Steam's default picture for the life of the install. The backend
    // answers "already there" from Steam's grid directory, so a settled device pays four
    // file checks per emulator and no request at all.
    art += await applyEmulatorArtwork(row, appId);
    appIds.push(appId);
  }

  if (appIds.length > 0) {
    await createOrUpdateEmulatorCollection(catalogue.collection, appIds);
  }
  logInfo(`Emulator collection "${catalogue.collection}": ${added} added, ${existing} present, ${art} images applied`);
  return { collection: catalogue.collection, added, existing, art, total: appIds.length };
}
