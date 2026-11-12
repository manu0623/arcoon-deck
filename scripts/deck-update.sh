#!/usr/bin/env bash
# Pull this repo on the Steam Deck and install it as the plugin — one command.
#
#   ~/arcoon-src/scripts/deck-update.sh            # pull, install, restart the loader
#   ~/arcoon-src/scripts/deck-update.sh --stage     # pull and stage only; print where
#
# Why a script rather than a git hook: the plugin directory is root-owned, so the
# install is the one step that must ask for a password. Everything before it — the
# pull, the prune to the shipped subset, the launcher's mode — runs unprivileged.
#
# The tree is installed from `git archive` of a commit, never from the working copy:
# a half-finished edit in ~/arcoon-src can never reach the running plugin, and the
# file set is the one actually committed.
set -euo pipefail

SRC="${ARCOON_SRC:-$HOME/arcoon-src}"
REPO="${ARCOON_REPO:-git@github.com:manu0623/arcoon-deck.git}"
KEY="${ARCOON_DEPLOY_KEY:-$HOME/.ssh/arcoon_deploy}"
PLUGIN_DIR="${ARCOON_PLUGIN_DIR:-$HOME/homebrew/plugins/romm-tender}"

# The subset a Decky plugin needs at runtime. `dist/` is here because this fork
# ships the built frontend instead of building it on the Deck.
SHIPPED=(plugin.json main.py package.json LICENSE README.md dist defaults bin assets py_modules scripts)

export GIT_SSH_COMMAND="ssh -i $KEY -o StrictHostKeyChecking=accept-new"

if [ ! -x "$KEY" ]; then
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
before=$(git -C "$SRC" rev-parse --short HEAD)

stage=$(mktemp -d "${TMPDIR:-/tmp}/arcoon-stage.XXXXXX")
git -C "$SRC" archive --format=tar HEAD -- "${SHIPPED[@]}" | tar -x -C "$stage"
chmod 755 "$stage/bin/rom-launcher"
version=$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$stage/plugin.json" | head -1)

echo "staged $version from $before at $stage"
if [ "${1:-}" = "--stage" ]; then
  exit 0
fi

backup="$HOME/romm-tender-backup-$(date +%Y%m%d-%H%M).tgz"
tar czf "$backup" -C "$(dirname "$PLUGIN_DIR")" "$(basename "$PLUGIN_DIR")" 2>/dev/null || true
echo "backup: $backup"

echo "installing (this is the step that needs the password)"
sudo rm -rf "$PLUGIN_DIR"
sudo cp -a "$stage" "$PLUGIN_DIR"
rm -rf "$stage"
sudo systemctl restart plugin_loader
echo "installed $version — Decky is reloading"
