# Where Your Data Lives

Arcoon Deck keeps everything it knows about your library in two folders under your own home directory:

| Folder                        | What is in it                                                                                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `~/.config/romm-tender/`      | Your settings — server address, sign-in, which platforms and collections you sync                                                                                         |
| `~/.local/share/romm-tender/` | The library database, cached cover art and artwork, playtime and save-sync state — and the small `bin/rom-launcher` file every one of your Steam shortcuts starts through |

Your **games** are not in either of them. Downloaded ROMs, BIOS files and save files live in RetroDECK's own folders,
exactly as before, and nothing on this page moves them.

## Why It Moved

Earlier versions kept this data inside Decky's plugin folders. Decky names those folders after the plugin's own folder
name, and that name is not something the plugin chooses — so when that folder name changed at version 0.31.0
(`decky-romm-sync` to `romm-tender`), every user's data quietly moved with it, and a freshly updated install opened on
an empty library while everything was still sitting in the old folder.

Putting the two folders under your home directory ends that: their names are fixed (`romm-tender`) rather than following
however Decky packages the plugin, so a future rename of the plugin folder cannot move them again.

## What Happens When You Update

The first time you start the new version, Arcoon Deck **copies** your data into the two folders above. Nothing is moved and
nothing is deleted — the old folders stay exactly where they are, with everything still in them. Once the copy has
finished, Arcoon Deck reads and writes your library and settings only in the new folders, and it does not open the old
database again on any later start.

On the maintainer's Steam Deck the copy took about four seconds for 268 MB. You do not have to do anything, and there is
no button to press.

### The old folders can be deleted

There are **two** of them per install, and each gets a `README.txt` saying when the copy happened and where it went:

- `~/homebrew/settings/<folder>` — the settings that were copied
- `~/homebrew/data/<folder>` — the library, covers and artwork that were copied

`<folder>` is `decky-romm-sync` or `romm-tender`, depending on which version of the plugin wrote them. They are spares:
Arcoon Deck no longer reads your library or settings from either, so you can delete them once you are happy that everything
is still there. Leaving them alone is also fine — they cost disk space and nothing else. If Arcoon Deck left no `README.txt`
in a folder, it did not copy from it, and there is nothing there it moved.

!!! warning "This is not the same as the old plugin"

    If Decky still lists an older **"RomM Sync"** plugin, that is a separate thing from the folders above, with its own
    card in the panel — and the card is what says whether it can go yet. Removing it before it does can stop your games
    from starting. See [Updating from a release before 0.31.0](getting-started.md#updating-from-a-release-before-0310).

## "Arcoon Deck found two copies of your library"

If you have used both the old and the new plugin folder, there may be **two** libraries on disk — and Arcoon Deck will not
guess which one you want. It leaves both alone, keeps running from the one it was given, and shows a card on the panel's
main page with a **Choose a copy** button.

The button opens a list of both copies, with where each one is, how big it is and when it last changed. A copy that has
since been deleted is still listed, saying so, rather than quietly leaving you with one option. Pick one and Arcoon Deck
records your choice; the copy itself happens the next time Arcoon Deck starts, because it cannot copy a database it is
currently using. Restarting your Steam Deck is the surest way to get there, and the dialog offers a **Restart device
now** button so you can get it over with — it asks you to confirm first, because it closes your games and reboots the
whole device, not just Steam.

Nothing changes until that restart: Arcoon Deck keeps using the copy it started with, and until then you can open the card
again and pick the other one instead.

Whichever you pick, the other copy is left untouched on disk.

## "Arcoon Deck could not move your data"

If the copy fails — a full disk, a folder that cannot be written — Arcoon Deck says so on the main page, with the reason, and
keeps reading and writing whichever folders it could not move out of. Nothing is lost and nothing is half-copied: it
simply tries again the next time Arcoon Deck starts. Freeing up disk space is usually all that is needed.

The card also appears while the RetroDECK-migration page is showing, because leaving that page takes an action of your
own and you would otherwise not see this until afterwards.

## Settings and the database are separate

The two folders are filled independently, so it is possible (though unusual) for your settings to have moved while the
database has not, or the other way round. That is normal: whichever half did not make it is retried on the next start,
and until then Arcoon Deck reads it from where it still is.
