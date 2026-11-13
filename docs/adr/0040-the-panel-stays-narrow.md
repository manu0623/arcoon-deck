# 0040 — The panel stays narrow, and every page is one column

## Status

Accepted. Supersedes the layout half of ADR-0029 for this fork.

## Context

ADR-0029 widened the QAM from Steam's 348 px to 854 px by driving Steam's own Friends-tab
expansion, so that a page could put a list beside a detail. On the Deck, 854 px is the whole
screen: a wide page covers the viewport rather than sitting in the panel, and the panel's
own contents change width under the reader. Everything that went with it — the injected
`max-width` rule, the measured overhang, the two-column `ListDetail`, the drill-down
fallback for when the widening silently stopped taking effect — existed to manage a surface
the reader never asked for.

## Decision

This fork keeps the QAM at **Steam's own width** and lays every page out in **one column**.

- `WidePage` no longer calls `useWideQamPanel`, so no page asks Steam to expand, no
  stylesheet is injected, and no `QamFriendsExpanded` message is posted. The width module
  and its dismount cleanup stay in place, because they only ever clear what this plugin
  itself set.
- `Columns` stacks what a page calls its columns, in the order the page names them. Each
  column still gets its own scrolling region, so the stacking is the page's order rather
  than one merged scroller. `width` is accepted and ignored: in one column the width is
  the column.
- `ListDetail` puts the detail **under** the list in the same scroller, separated by a
  hairline. Focus still selects, exactly as before, so no page's selection behaviour
  changed — only where the detail is painted.

## Consequences

- Every page fits the panel a reader already sees. Nothing is clipped, nothing covers the
  screen, and the "+" expansion a QAM user may have seen before is gone.
- `ListDetail`'s two-column tests and `WidePage`'s expansion test were rewritten to the new
  intent rather than deleted: the frame is now pinned to *not* posting the expansion
  message, and the layout to *not* being two columns.
- The measured-height machinery in `WidePage` stays. It sizes the body to the panel's real
  height either way, and it was never specific to a wide panel — only its comments about
  the first measurement talked about widening.
- Sync's table-beside-controls page is now table-above-controls. Its own tests still pass,
  because what they assert is what each region renders, not where it sits.
