#!/usr/bin/env bash
# The privileged half of a Deck update: put an already-staged tree in place and
# restart the loader. Installed as /usr/local/bin/arcoon-install and allow-listed
# in /etc/sudoers.d/arcoon-install, so an update needs no password and no terminal
# on the Deck.
#
# **It takes no arguments on purpose.** A passwordless root command that accepts a
# path is a passwordless root copy-anything command; this one reads exactly one
# place — the staging directory the unprivileged updater fills — and refuses
# anything else. The source is therefore fixed here rather than passed in.
set -euo pipefail

STAGE="/home/deck/arcoon-stage"
PLUGIN_DIR="/home/deck/homebrew/plugins/romm-tender"
PLUGINS_ROOT="/home/deck/homebrew/plugins"

if [ "$(id -u)" -ne 0 ]; then
  echo "arcoon-install: must run as root" >&2
  exit 1
fi
if [ ! -f "$STAGE/plugin.json" ] || [ ! -f "$STAGE/main.py" ]; then
  echo "arcoon-install: no staged plugin at $STAGE (run scripts/deck-update.sh)" >&2
  exit 2
fi

version=$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$STAGE/plugin.json" | head -1)
backup="/home/deck/romm-tender-backup-$(date +%Y%m%d-%H%M%S).tgz"
if [ -d "$PLUGIN_DIR" ]; then
  tar czf "$backup" -C "$PLUGINS_ROOT" romm-tender 2>/dev/null || true
fi

rm -rf "$PLUGIN_DIR"
cp -a "$STAGE" "$PLUGIN_DIR"
chown -R root:root "$PLUGIN_DIR"
chmod 755 "$PLUGIN_DIR/bin/rom-launcher"

systemctl restart plugin_loader
echo "arcoon-install: installed $version, backup at $backup"
