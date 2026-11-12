#!/usr/bin/env bash
# Pull this repo on the Steam Deck and install it as the plugin — one command.
#
#   ~/arcoon-src/scripts/deck-update.sh            # pull, install, restart the loader
#   ~/arcoon-src/scripts/deck-update.sh --stage     # pull and stage only; print where
#
# Two halves, because the plugin directory is root-owned and this part is not:
# everything here runs as `deck` (the pull, the prune to the shipped subset, the
# launcher's mode), and then one privileged command puts the result in place.
#
# Where `/usr/local/bin/arcoon-install` is installed and allow-listed in sudoers
# (see docs/contributing/deck-updates.md), that command needs no password — which
# is what lets an update be pushed to the Deck from somewhere else entirely. Where
# it is not, the same work is inlined here and asks for the password.
#
# The tree is installed from `git archive` of a commit, never from the working copy:
# a half-finished edit in ~/arcoon-src can never reach the running plugin, and the
# file set is the one actually committed.
set -euo pipefail

SRC="${ARCOON_SRC:-$HOME/arcoon-src}"
REPO="${ARCOON_REPO:-git@github.com:manu0623/arcoon-deck.git}"
KEY="${ARCOON_DEPLOY_KEY:-$HOME/.ssh/arcoon_deploy}"
PLUGIN_DIR="${ARCOON_PLUGIN_DIR:-$HOME/homebrew/plugins/romm-tender}"

# A fixed staging path, not a temporary one: the privileged half reads exactly this
# directory and takes no arguments, which is what makes it safe to allow-list
# without a password. `scripts/deck-install-root.sh` states that in full.
STAGE="$HOME/arcoon-stage"

# The subset a Decky plugin needs at runtime. `dist/` is here because this fork
# ships the built frontend instead of building it on the Deck.
SHIPPED=(plugin.json main.py package.json LICENSE README.md dist defaults bin assets py_modules scripts)

export GIT_SSH_COMMAND="ssh -i $KEY -o StrictHostKeyChecking=accept-new"

if [ ! -f "$KEY" ]; then
  echo "no deploy key at $KEY — generate one with: ssh-keygen -t ed25519 -N '' -f $KEY" >&2
  exit 1
fi

if [ ! -d "$SRC/.git" ]; then
  echo "first run: cloning $REPO into $SRC"
  git clone --quiet "$REPO" "$SRC"
  git -C "$SRC" config core.sshCommand "ssh -i $KEY"
fi

echo "pulling $SRC"
git -C "$SRC" pull --quiet --ff-only
head=$(git -C "$SRC" rev-parse --short HEAD)

rm -rf "$STAGE"
mkdir -p "$STAGE"
git -C "$SRC" archive --format=tar HEAD -- "${SHIPPED[@]}" | tar -x -C "$STAGE"
chmod 755 "$STAGE/bin/rom-launcher"
version=$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$STAGE/plugin.json" | head -1)

echo "staged $version from $head at $STAGE"
if [ "${1:-}" = "--stage" ]; then
  exit 0
fi

# Where the allow-listed installer can live. `/usr/local` is on SteamOS's read-only
# root image — installing there means disabling the immutable filesystem for the whole
# machine, which its own updates then trample — so the writable partition's
# `/var/lib/arcoon` is the real location and `/usr/local/bin` is only a courtesy for
# other systems.
INSTALLER=""
for candidate in "${ARCOON_INSTALLER:-}" /var/lib/arcoon/arcoon-install /usr/local/bin/arcoon-install; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    INSTALLER="$candidate"
    break
  fi
done

if [ -n "$INSTALLER" ]; then
  # Allow-listed, so no password and no terminal on the Deck: this is the path that
  # makes an update pushable from another machine.
  sudo -n "$INSTALLER"
else
  echo "installing (this is the step that needs the password)"
  sudo rm -rf "$PLUGIN_DIR"
  sudo cp -a "$STAGE" "$PLUGIN_DIR"
  sudo systemctl restart plugin_loader
  echo "installed $version — Decky is reloading"
fi
