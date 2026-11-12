# Updating the Deck from Git

The plugin is installed on the Deck by pulling this repository, not by building an
installer. `dist/` is committed here for exactly that reason: the Deck has no Node
toolchain, and a plugin without its built frontend cannot load.

## One-time setup

A private repo needs credentials on the Deck. The Deck gets its own read-only deploy key,
so no account token is ever written to disk in plain text and revoking it touches only this
one machine:

```sh
ssh-keygen -t ed25519 -N "" -C "arcoon-deck-pull" -f ~/.ssh/arcoon_deploy
git clone git@github.com:manu0623/arcoon-deck.git ~/arcoon-src
git -C ~/arcoon-src config core.sshCommand "ssh -i $HOME/.ssh/arcoon_deploy"
```

Then run `bash ~/arcoon-src/scripts/deck-update.sh` once. It pulls, stages the shipped
subset, backs up the current plugin and installs — asking for the password only for the
install itself.

## Every update after that

```sh
bash ~/arcoon-src/scripts/deck-update.sh
```

`--stage` stops after staging and prints the directory, for inspecting what would ship
without touching the running plugin.

## What the script does and does not touch

It installs from `git archive HEAD` — a committed tree, never a working copy — so an
uncommitted edit in `~/arcoon-src` cannot reach the plugin. It replaces only the plugin
directory; user data lives under `~/.local/share/romm-tender` and `~/.config/romm-tender`
(ADR-0031) and is never part of the install. Each run also leaves a
`~/romm-tender-backup-<timestamp>.tgz` of the previous plugin directory.
