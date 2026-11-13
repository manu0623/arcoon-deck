# 47. A game that lands without a save adopts the one the server has

**Status:** Accepted (0.38.0)

## The problem

The slot wizard asked a question before the first launch of every new game, and
the answer could only go one way when the machine held no save. With save sync
off by default besides, a freshly downloaded game launched from an empty state
while the save the user had played on their desktop sat on the server — the
exact trip the app exists to remove.

The wizard is not wrong in general. Two saves that both exist and disagree is
the user's decision, and guessing there would trade a prompt for silent loss.

## The decision

`get_save_setup_info` recommends one of three actions from the state it already
reads, and the frontend obeys whichever comes back:

| this machine | server | recommendation |
| --- | --- | --- |
| no save | newest save in a named slot | `auto_adopt_server` (with `auto_slot`) |
| a save | no slots | `auto_confirm_default` (unchanged) |
| a save | slots | `show_wizard` (unchanged) |

Adoption is the ordinary confirm with `migrate=False`: it is a metadata flip,
no files move, and the sync that follows pulls the save. A new callable,
`auto_adopt_server_slot`, performs it, and it is scheduled when a download
completes so the game is already current before the user presses Play. The
launch path asks the same question again, so a download that finishes while the
plugin was unloaded still ends up pointing at the server's save.

Two things the server cannot make us guess:

- **A legacy save (`slot: null`) is never adopted.** It is a migration source
  with no slot to confirm; the wizard still offers to migrate it.
- **An unproven server view is never adopted.** A failed query refuses rather
  than reading the empty list as "the server has nothing". The same rule that
  keeps `auto_confirm_default` off a timeout keeps adoption off it.

The newest slot is chosen by instant, not by string: `latest_updated_at` is
compared after parsing, so `13:00+02:00` loses to `12:00Z`.

`save_sync_enabled` now ships on. Adoption is worth little if the sync it sets
up is disabled, and a default that must be turned on first makes every first
launch a setup chore. A settings dict that never went through `load_settings`
still reads as off — absence there is not the shipped default, and the
harnesses that construct one are the reason the seam keeps that fallback.

## Consequences

- The wizard appears only when the local and the server state genuinely
  disagree, which is the only case where its question has an answer the code
  cannot derive.
- A download is now a save workload: one extra `list_saves` per finished game,
  scheduled rather than awaited, so a slow server delays nothing.
- Rolling back a slot choice stays the user's: adoption does nothing when a
  slot is already confirmed, even if a newer save appeared elsewhere.
