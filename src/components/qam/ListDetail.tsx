/**
 * The list-and-detail layout of a QAM page, in ONE column: the list, and the
 * focused entry's detail directly under it.
 *
 * Two side-by-side columns need the panel Steam only widens for its own Friends
 * view (ADR-0029), and this fork keeps the panel at Steam's own 348 px — so the
 * detail goes below the list instead of beside it. One column, one scroller, and
 * nothing painted outside the panel a reader already sees.
 *
 * Focus still SELECTS, as Steam's own settings do: moving through the list
 * changes the detail below it at once, and the detail travels with the rows
 * rather than being reached by a second key. That is why the list keeps its
 * `onFocus` handler: with a single pane there is no drill-down to open, and the
 * row a reader lands on is the row whose detail they want.
 *
 * A region scrolls by moving focus, so what a reader must reach — a detail's
 * table rows included — has to be focusable; plain text scrolls along with the
 * row it accompanies but cannot be scrolled to.
 *
 * Selection is controlled: the page owns `selectedId` and decides what a change
 * means for the rest of it.
 *
 * Because focus selects, where the page OPENS decides what it opens on: entry
 * focus landing on the first row selects that row and overwrites the selection
 * the page was opened with. So the selected row declares itself the area entry
 * focus belongs in ({@link ENTRY_STOP_ATTR}) and the frame places focus there.
 */

import { type FC, type ReactNode } from "react";
import { Focusable } from "@decky/ui";
import { ENTRY_STOP_ATTR } from "../../utils/entryFocus";

export interface ListDetailItem {
  id: string;
  render: (selected: boolean) => ReactNode;
}

export interface ListDetailProps {
  items: ListDetailItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  renderDetail: (selectedId: string | null) => ReactNode;
  /**
   * Controls that act on the whole list — Enable all, Disable all — and anything
   * that speaks for the list as a whole, such as a status line about one of
   * those writes. Rendered above the first row and scrolling with it, outside
   * every item, so focusing one reports no selection: these belong to the list,
   * not to a row of it.
   */
  listHeader?: ReactNode;
  /**
   * Makes every row wrapper a focus stop by giving it an activate handler, for
   * a list whose rows carry no control of their own — a label and nothing else.
   * Without it such a row is a bare container that passes focus to children it
   * does not have, so the reader cannot reach it and cannot scroll past it.
   *
   * Off by default, because a row that DOES carry a control must leave A to it.
   */
  selectOnActivate?: boolean;
}

export const ListDetail: FC<ListDetailProps> = ({
  items,
  selectedId,
  onSelect,
  renderDetail,
  listHeader,
  selectOnActivate,
}) => (
  <div style={{ height: "100%", minHeight: 0, overflowY: "auto" }}>
    <Focusable flow-children="vertical">
      {listHeader}
      {items.map((item) => (
        // The declaration sits on a wrapper rather than on the row itself:
        // `Focusable` takes its own props and nothing establishes that it passes
        // an unknown one to the DOM. `display: contents` keeps the wrapper out of
        // the layout — it carries the attribute and nothing else.
        <div
          key={item.id}
          style={{ display: "contents" }}
          {...(item.id === selectedId ? { [ENTRY_STOP_ATTR]: "" } : {})}
        >
          <Focusable
            onFocus={() => {
              if (item.id !== selectedId) onSelect(item.id);
            }}
            {...(selectOnActivate ? { onActivate: () => onSelect(item.id) } : {})}
          >
            {item.render(item.id === selectedId)}
          </Focusable>
        </div>
      ))}
    </Focusable>
    {/* The detail follows the list in the same column: one scroller, so a long
        detail is reached by scrolling past the rows rather than by leaving the
        list. A hairline and a little air are what separate the two halves now
        that a column edge no longer does it. */}
    <div style={{ borderTop: "1px solid rgba(255, 255, 255, 0.12)", marginTop: "8px" }}>
      <Focusable flow-children="vertical">{renderDetail(selectedId)}</Focusable>
    </div>
  </div>
);
