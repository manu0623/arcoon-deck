# Getting Started

## What is Arcoon Deck?

Arcoon Deck is a [Decky Loader](https://decky.xyz/) plugin that connects your self-hosted
[RomM](https://github.com/rommapp/romm) ROM library to Steam. Every game in your RomM library appears as a Non-Steam
shortcut in the Steam Library, complete with cover art, metadata, and collections. The plugin also installs what the
games need: it downloads the libretro core a platform requires and the standalone emulator a game names, into its own
tree under your home directory. No emulator has to be installed beforehand, and
[RetroDECK](https://retrodeck.net/) is optional — supported as an opt-in runtime, not a prerequisite.

## Prerequisites

Before installing the plugin, you need:

1. **A RomM server** — a running RomM instance with your ROM library. You'll need the server URL plus a username and
   password to connect the first time. The plugin exchanges those credentials for a RomM Client API Token and stores
   only the token — your password is never saved. Each user should have their own RomM account (see
   [Save Sync](save-sync.md) for why this matters).

2. **Nothing else for emulation** — the plugin downloads RetroArch and the libretro cores it launches with, and
   installs the standalone emulators a game needs. If you already keep a library in
   [RetroDECK](https://retrodeck.net/), that is supported too, as an opt-in runtime.

3. **Decky Loader** — the plugin framework. Install it from [decky.xyz](https://decky.xyz/) if you haven't already.
   Decky renders inside Steam's gamepad UI, and the plugin works wherever that UI runs: Gaming Mode on the Steam Deck,
   or Big Picture Mode on a Linux PC/HTPC — a dedicated Game Mode session is not required.

4. **A personal RomM account** — save sync ties saves to the authenticated user. Use your own account, not a shared one.

## Installation

**Not on the Decky store.** The store doesn't accept plugins whose code is written with AI assistance, and Arcoon Deck's is —
see [How this is built](../index.md). Install it from a zip you build, below.

### From a zip you build (this fork's only route today)

**This fork has no published releases yet**, so build the plugin and install the file:

1. On a machine with [Decky CLI](https://github.com/SteamDeckHomebrew/cli) — the Deck itself is fine:
   `git clone https://github.com/manu0623/arcoon-deck.git && cd arcoon-deck && decky plugin build`
2. Open the Quick Access Menu (QAM) in Gaming Mode, go to the Decky Loader tab (the plug icon), open settings
   (gear icon), and under **General → Other** enable **Developer mode** — a **Developer** tab appears
3. Open that **Developer** tab and choose **Install Plugin from ZIP File**
4. Pick the zip Decky CLI wrote to `out/` — the plugin appears in the QAM, no restart needed

**Install from URL** works the same way once a release exists here: open this fork's
[releases page](https://github.com/manu0623/arcoon-deck/releases), copy the zip asset's address, and paste it into
**Install Plugin from URL**. Pasting the newest asset's URL again later is how you update.

Decky reads the plugin's name from the file name it installs, so the asset has to be named `Arcoon Deck.zip`
exactly: a differently named file is treated as a different plugin rather than as an update to this one. Tender's
releases carry `Tender.zip` because that was the name then — the file name is what Decky records either way.

Any direct URL to the zip file works (GitHub releases, a self-hosted mirror, etc.) as long as it points to a valid
`.zip` containing the plugin.

### Updating from a release before 0.31.0

Releases up to 0.30.1 install into a folder named `decky-romm-sync`; from 0.31.0 on the folder is named `romm-tender`.
Decky treats a differently-named folder as a different plugin, so updating across that boundary leaves you with **two**
entries: the older one still shown as **RomM Sync**, and the new one as **Arcoon Deck**.

**Wait for Arcoon Deck to say the older plugin can go.** Every Steam shortcut this plugin created used to launch through a
file inside that older plugin's folder. Arcoon Deck now keeps its own copy of that file outside any plugin folder and points
your shortcuts at it, which it does shortly after Steam starts — but until it has, removing "RomM Sync" stops all of
your games from starting, and nothing in Arcoon Deck can put the file back.

While both are installed, Arcoon Deck's QAM panel carries a card that tells you which of those it is — including when the
panel is showing a server-version error or a pending RetroDECK migration instead of its usual contents, the two states
in which the older plugin looks most like something to clear away. The card says one of two things:

- **"RomM Sync" is still installed, and your games need it** — the move has not happened yet on this device. Leave the
  older plugin alone. Arcoon Deck tries again every time it starts up, which is when your device does — restarting Steam
  itself is not enough, because that reloads the panel without starting Arcoon Deck's own half again.
- **"RomM Sync" can be removed now** — nothing in Arcoon Deck depends on it any more. Remove it wherever Decky lists your
  installed plugins, or keep it: it costs disk space and nothing else. This one has a **Dismiss**, and dismissing it is
  remembered — the card does not come back at the next start.

The new install also starts with its own empty settings and library, because Decky gave each plugin folder its own data
location — your existing settings and synced library are in the older install until Arcoon Deck brings them across.

### Manual installation (alternative)

1. Build the plugin's `.zip` (`decky plugin build`) or download it from this fork's
   [releases page](https://github.com/manu0623/arcoon-deck/releases) once one is published
2. Extract the zip to `~/homebrew/plugins/` on your device (via SSH, file manager, or USB)
3. Restart Decky Loader — either reboot, or run `sudo systemctl restart plugin_loader` via SSH
4. The plugin appears in your QAM under the Decky tab

## First-Time Setup

After installation, you need to connect the plugin to your RomM server:

1. Open the QAM and find **Arcoon Deck**
2. Tap **Settings** in the menu, then **Connections** in the section list on the left
3. Enter your RomM server URL (e.g. `http://192.168.1.100:8080`) — this saves automatically
4. Tap **Sign in**, enter your RomM username and password once, and confirm
5. The **RomM Account** row shows **Signed in** on success. The plugin's main QAM panel has a **Connection** row that
   shows the live connection status whenever you open it — there is no separate test button

On a controller you can confirm a text field with the on-screen keyboard's **Enter** key (or the **R2** shortcut)
instead of navigating to the button — for example save-slot names and the artwork search. In the sign-in dialog, Enter
moves from the username to the password field and confirms only once every required field is filled; an incomplete form
can't be submitted, and **Cancel** leaves your existing sign-in untouched.

The plugin mints a RomM Client API Token from the credentials you enter and discards the password — it is never stored.
The same applies if the plugin auto-migrates an older install that still had a saved password: the password is discarded
as soon as a token is minted. If your RomM account is not allowed to create API tokens, the sign-in step reports that
and you'll need an account with token permissions.

<!-- Screenshot: Connection Settings page with URL field, Sign in button, and token status -->

Once connected, you're ready to sync your library. See [Configuration](configuration.md) for additional settings, or
jump straight to [Syncing Your Library](syncing-your-library.md).

---

**Next:** [Configuration](configuration.md)

## Updating the plugin

The installed folder belongs to root, and a Deck in Game Mode has no terminal to type a password into — so the
panel updates itself instead. **Settings → Advanced → Update from URL** takes the address of a plugin zip built
from this repository, installs it and lets Decky restart the loader. Nothing else is needed: no Desktop mode, no
password.

What it will refuse, and why each refusal exists:

- **A build that is not newer.** `plugin.json`'s version is compared against the running one, so re-installing the
  same build is not an update.
- **A zip for another plugin, or one that unpacks into a different folder.** Decky derives this plugin's settings,
  data and logs from the folder name, so a differently named folder looks like a fresh plugin and loses the
  library.
- **A zip missing `main.py`, `plugin.json`, `dist/index.js` or the bootstrap modules.** It would not run, and the
  code doing the swap is the code being swapped.

The old folder is kept until the new one is unpacked and holds its `plugin.json`; if the swap fails the old folder
goes back.
