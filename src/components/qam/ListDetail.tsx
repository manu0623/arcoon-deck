/**
 * The list-and-detail layout of a wide QAM page: the list on the left, the
 * focused entry's detail on the right, each scrolling on its own inside the
 * frame's measured height. It is `Columns` with those two columns.
 *
 * A region scrolls by moving focus, so what a reader must be able to reach in
 * either pane — a detail's table rows included — has to be focusable; plain
 * text scrolls along with the row it accompanies but cannot be scrolled to.
 *
 * Focus selects — moving through the list changes the detail at once, as Steam's
 * own settings do. The row's own control keeps A, so this component intercepts
 * it only where a page asks for `selectOnActivate`, for rows that carry no
 * control; a row that carries a toggle still toggles on press. A control that
 * acts on the whole list goes in `listHeader` rather than in a row, so reaching
 * it reports no selection.
 *
 * Selection is controlled: the page owns `selectedId` and decides what a change
 * means for the rest of it.
 *
 * Because focus selects, where the page OPENS decides what it opens on: entry
 * focus landing on the first row selects that row and overwrites the selection
 * the page was opened with. So the selected row declares itself the area entry
 * focus belongs in ({@link ENTRY_STOP_ATTR}) and the frame places focus there.
 *
 * **Narrow panels drill down instead.** Two columns need the panel Steam only
 * widens for its own Friends view (ADR-0029). Where that widening does not
 * take — an internal that moved, a Decky build whose probe answers nothing —
 * the panel stays ~348 px, the fixed-width list fills it and the detail is a
 * sliver: measured on Decky 3.3.1, the detail pane was 60 px and every row
 * began with one letter. So below {@link TWO_COLUMN_MIN_WIDTH} the same
 * selection is shown one pane at a time: the list, then the entry's detail with
 * a Back row. Which pane is showing is local state, NOT the page's selection —
 * the page still owns what is selected, and a wide panel behaves exactly as
 * before.
 */

import { useEffect, useRef, useState, type FC, type ReactNode } from "react";
import { ButtonItem, Focusable, PanelSectionRow } from "@decky/ui";
import { debugLog } from "../../api/backend";
import { ENTRY_STOP_ATTR } from "../../utils/entryFocus";
import { Columns } from "./Columns";

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

// The list takes about a third of the 806 px a wide tab panel offers.
const LIST_WIDTH = "264px";

// Below this the two columns stop being readable: the list is fixed at
// `LIST_WIDTH` and the panel's narrow width is 348 px, which leaves the detail a
// sliver. 520 is where the detail still gets ~200 px, the narrowest that shows a
// label and a value.
const TWO_COLUMN_MIN_WIDTH = 520;

export const ListDetail: FC<ListDetailProps> = ({
  items,
  selectedId,
  onSelect,
  renderDetail,
  listHeader,
  selectOnActivate,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [narrow, setNarrow] = useState(false);
  const [drilled, setDrilled] = useState<string | null>(null);
  const lastReport = useRef("");

  // Measured from the container rather than the window: the panel is its own
  // box, and the widening this page asks for lands on an ancestor's `max-width`,
  // so a window width would answer the wrong question.
  useEffect(() => {
    const node = containerRef.current;
    const view = node?.ownerDocument.defaultView;
    if (!node || !view) {
      return;
    }
    // The panel is the box that CLIPS us, and it is the smaller of the two
    // whenever the widening has stopped taking effect — Steam's QAM cap is
    // Steam's, and it has changed under this plugin before. Our own width then
    // still reads wide, two columns are chosen from it, and the detail column is
    // painted outside the visible panel: the reader sees the section list and a
    // section with no content in it. Deciding from the narrower of the two boxes
    // keeps the fallback reachable in exactly that case, and answers the same as
    // before whenever the widening works (both boxes wide) or the panel is
    // genuinely wide.
    const panel = node.closest<HTMLElement>('[id^="quickaccess_content_"]');
    // 0 means "not laid out yet" — the first frame before Steam sizes the panel,
    // and every jsdom render. Answering "narrow" there would flash the fallback
    // on a wide panel and would make the component untestable in its wide form.
    const measure = () => {
      const width = node.clientWidth;
      const panelWidth = panel?.clientWidth ?? 0;
      const available = panelWidth > 0 ? Math.min(width > 0 ? width : panelWidth, panelWidth) : width;
      const nextNarrow = available > 0 && available < TWO_COLUMN_MIN_WIDTH;
      setNarrow(nextNarrow);
      // Logged on change only: this runs per resize, and a debug log per frame
      // would bury the thing the number is there to answer.
      const report = `${panelWidth}x${width}`;
      if (report !== lastReport.current) {
        lastReport.current = report;
        void debugLog(`ListDetail: panel=${panelWidth} container=${width} narrow=${nextNarrow}`);
      }
    };
    measure();
    const observer = new view.ResizeObserver(measure);
    observer.observe(node);
    if (panel) {
      observer.observe(panel);
    }
    return () => observer.disconnect();
  }, []);

  // Narrow rows are drilled into rather than merely focused, so A reports the
  // selection and opens the entry. Focus-select would jump a reader into the
  // detail the moment they scrolled the list, which is the wide panel's idiom,
  // not a one-pane one.
  const openRow = (id: string) => {
    onSelect(id);
    setDrilled(id);
  };

  const rows = () => (
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
            {...(narrow
              ? { onActivate: () => openRow(item.id) }
              : {
                  onFocus: () => {
                    if (item.id !== selectedId) onSelect(item.id);
                  },
                  ...(selectOnActivate ? { onActivate: () => onSelect(item.id) } : {}),
                })}
          >
            {item.render(item.id === selectedId)}
          </Focusable>
        </div>
      ))}
    </Focusable>
  );

  if (narrow) {
    return (
      <div ref={containerRef} style={{ height: "100%", minHeight: 0, overflowY: "auto" }}>
        {drilled === null ? (
          rows()
        ) : (
          <Focusable flow-children="vertical" style={{ height: "100%", overflowY: "auto" }}>
            <PanelSectionRow>
              <ButtonItem layout="below" onClick={() => setDrilled(null)}>
                ‹ Back
              </ButtonItem>
            </PanelSectionRow>
            <Focusable flow-children="vertical">{renderDetail(drilled)}</Focusable>
          </Focusable>
        )}
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ height: "100%", minHeight: 0 }}>
      <Columns
        columns={[
          {
            id: "list",
            width: LIST_WIDTH,
            content: rows(),
          },
          {
            id: "detail",
            // Keyed on the selection so a new entry's detail opens at its own top.
            // Focus is in the list when this changes — that is what changed the
            // selection — so nothing focused is unmounted.
            regionKey: selectedId ?? "",
            content: <Focusable flow-children="vertical">{renderDetail(selectedId)}</Focusable>,
          },
        ]}
      />
    </div>
  );
};
