# 75. An update comes from the project's own repository

- **Status:** Accepted (0.48.55)
- **Supersedes:** nothing; extends the self-update path the panel already had
- **Follows:** 0039 (the plugin installs its own runtime)

## Context

The panel can replace its own folder, which is the only passwordless way to update on a
Deck in Game Mode. Until now it needed an address: a zip had to be built, hosted, and
its link pasted into a field — an act of bookkeeping that a person updating one device
does by hand and forgets on the second.

The question this record answers is what the field should do when it is left empty.

## Decision

An empty address installs the newest build of this project from its own repository —
`https://github.com/manu0623/arcoon-deck/archive/refs/heads/main.zip` — so an update is
one press and follows the last push, with no release step, asset name or hosted link to
keep in step. A pasted address still takes precedence, because a build from a mirror or a
test build has to remain installable.

A source archive is not the shape the installer accepts, so it is re-rooted before
validation: its single top folder (`arcoon-deck-main/`) becomes the plugin's own folder
name (`romm-tender/`), and only the subset a plugin needs at runtime is carried. Total
files, docs and CI never reach the Deck.

## Consequences

- Everything the installer refuses still applies unchanged: the folder name, the plugin
  name, a strictly newer version, and the entries without which a build cannot start.
  The default source is not a way around validation, only a way to skip the address.
- The repository has to be publicly readable, because the download carries no
  credentials. A private fork makes this path answer 404 and leaves the paste field as
  the working route.
- `main` is the source of truth rather than a release, so a build installed this way is
  whatever was last pushed. `dist/index.js` is committed, which is what lets a source
  archive be installable at all.
