# Updating the Deck from Git

The plugin is installed on the Deck by pulling this repository, not by building an
installer. `dist/` is committed here for exactly that reason: the Deck has no Node
toolchain, and a plugin without its built frontend cannot load.

An update has two halves. The first pulls and stages, and runs as `deck` — the pull, the
prune to the shipped subset, the launcher's mode. The second replaces the plugin directory,
which is root-owned, and restarts the loader. Only that second half needs privilege.

## One-time setup

A private repo needs a credential on the Deck. The Deck gets its own read-only deploy key,
so no account token is written to disk in plain text and revoking it touches only this one
machine:

```sh
ssh-keygen -t ed25519 -N "" -C "arcoon-deck-pull" -f ~/.ssh/arcoon_deploy
git clone git@github.com:manu0623/arcoon-deck.git ~/arcoon-src
git -C ~/arcoon-src config core.sshCommand "ssh -i $HOME/.ssh/arcoon_deploy"
```

### Allow-listing the privileged half

Install the root-owned half once and let sudo run that one command without a password. It
matters that the command takes **no arguments**: a passwordless root installer that accepted
a path would be a passwordless root copy-anything command. This one reads exactly
`~/arcoon-stage` and refuses anything else.

```sh
sudo mkdir -p /var/lib/arcoon
sudo cp ~/arcoon-src/scripts/deck-install-root.sh /var/lib/arcoon/arcoon-install
sudo chmod 755 /var/lib/arcoon/arcoon-install
echo 'deck ALL=(root) NOPASSWD: /var/lib/arcoon/arcoon-install' | sudo tee /etc/sudoers.d/zz-arcoon-install
sudo chmod 440 /etc/sudoers.d/zz-arcoon-install
```

**The `zz-` prefix is load-bearing.** SteamOS ships `/etc/sudoers.d/wheel` holding
`%wheel ALL=(ALL) ALL`, and sudo resolves a repeated match by the **last** rule rather than
the most specific one. A file named `arcoon-install` sorts before `wheel`, so wheel's
passworded rule is read afterwards and wins — the allow-list parses correctly, shows up in
`sudo -l`, and still asks for a password. Read last is the whole requirement.

**It cannot live in `/usr/local/bin`.** SteamOS mounts its root image read-only, so that
path answers `Read-only file system`, and writing there would mean disabling the immutable
filesystem for the whole machine — which a SteamOS update then overwrites. `/var` is the
writable partition, and the directory is root-owned, which is the property that matters: the
installer must not be a file the `deck` user can edit, or the allow-list would be a
passwordless root shell in disguise.

With that in place, `deck-update.sh` uses it and an update needs no password — which is what
makes an update pushable over SSH from another machine. Without it, the script inlines the
same work and asks for the password.

## Every update after that

```sh
bash ~/arcoon-src/scripts/deck-update.sh
```

`--stage` stops after staging and prints the version and commit it staged, for inspecting
what would ship without touching the running plugin.

## What the script does and does not touch

It installs from `git archive HEAD` — a committed tree, never a working copy — so an
uncommitted edit in `~/arcoon-src` cannot reach the plugin. It replaces only the plugin
directory; user data lives under `~/.local/share/romm-tender` and `~/.config/romm-tender`
(ADR-0031) and is never part of the install. Each install leaves a
`~/romm-tender-backup-<timestamp>.tgz` of the previous plugin directory.
