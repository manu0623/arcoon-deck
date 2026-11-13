# ADR-0055 — A flatpak this plugin provisions gets to read the files it launches

**Status:** accepted

## The problem

Provisioning installed an emulator and stopped there. The PCSX2 flatpak this plugin put
on the reference Deck carries only:

```
filesystems=xdg-config/kdeglobals:ro;xdg-run/gamescope-0:ro;
```

so `flatpak run net.pcsx2.PCSX2 -fullscreen -- "/home/deck/.local/share/romm-tender/roms/ps2/Sly Cooper and the Thievius Raccoonus (USA).iso"`
opened the emulator and reported no ROM at that location — while the ISO sat readable at
that exact path (2,802,319,360 bytes, same inode) and the plugin's own database recorded
it installed. Measured directly, inside that sandbox:

```
$ flatpak run --command=/usr/bin/ls net.pcsx2.PCSX2 -la /home/deck/.local/share/romm-tender/roms/ps2/
ls: cannot access '/home/deck/.local/share/romm-tender/roms/ps2/': No such file or directory
```

An emulator that cannot read the ROM it was installed to play is not installed, and no
launch-side fix can help: the sandbox is the boundary, not the command.

## The decision

**Provisioning grants the app `--filesystem=host` with `flatpak override --user`.** This is
the access EmuDeck grants every emulator flatpak it installs (`installEmuFP.sh:33`), so it
is the arrangement these emulators are actually tested against on this hardware.

It runs on every provisioning pass, not only on a fresh install: an app installed before
this rule existed is precisely the one that cannot see the ROM tree, so the already-present
branch re-applies the grant. `--user` writes the app's own override file, needs no password,
and a repeat call is a no-op.

The grant is reported, not folded into the install: both results carry
`sandbox_host_access`, because an install that happened and an access grant that did not
are different failures to tell a user about.

`host` is broad. The narrower alternatives were considered and rejected on measurement: this
Deck's standalone PCSX2 reads its BIOS from `~/Emulation/bios/Ps2`, outside the plugin's own
data tree, and folder-boot PS3 installs are read in place under the emulator's sandbox. A
grant cut to `~/.local/share/romm-tender` would have hidden the BIOS and broken the emulator
in a way that looks like a configuration error.

## What this does not do

- It does not grant anything to an emulator the plugin never provisions. A flatpak the user
  installed themselves keeps its own access; a launch that cannot see its ROM for that
  reason still fails, and the reason is now visible in the log line the adapter writes.
- It does not fix a *path* problem. A shortcut pointing at a file that is genuinely gone
  still fails, and the ROM still has to exist where the bake says it does.
