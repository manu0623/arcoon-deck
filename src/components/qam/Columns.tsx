/**
 * Where a page used to put its regions side by side, it now stacks them: ONE
 * column, in the order the page names them.
 *
 * The panel stays Steam's narrow width (348 px) — the plugin no longer asks
 * Steam to widen it — so two columns would leave each of them too narrow to
 * read. A page that describes its content as columns keeps saying so, and the
 * order it lists them in is the order a reader meets them.
 *
 * Each column keeps its own `ScrollRegion` and each region still scrolls on its
 * own: the stacked list is the page's column order, not one merged scroller.
 * `width` is accepted and ignored — in a single column the width is the column.
 *
 * Structure and vocabulary: `docs/architecture/qam-panel.md`.
 */

import type { FC, ReactNode } from "react";
import { Focusable } from "@decky/ui";
import { ScrollRegion } from "./ScrollRegion";

export interface Column {
  id: string;
  /** A fixed width, or nothing for the column that takes what is left. */
  width?: string;
  /**
   * What makes the page want this column REMOUNTED rather than re-rendered —
   * which is how a fresh region opens at its own top rather than at the offset
   * the previous content was left at. The key a region carries joins the
   * column's `id` to this, so a column that names none keeps one constant key
   * and is never remounted.
   *
   * A key rather than a ref that scrolls the region back: Steam's scroll panel
   * is reached through a webpack probe and nothing establishes that it forwards
   * one, while a key needs no handle on the element at all.
   */
  regionKey?: string;
  content: ReactNode;
}

export interface ColumnsProps {
  columns: Column[];
}

export const Columns: FC<ColumnsProps> = ({ columns }) => (
  <Focusable
    flow-children="vertical"
    style={{ display: "flex", flexDirection: "column", gap: "12px", height: "100%", minHeight: 0 }}
  >
    {columns.map((column) => (
      <ScrollRegion
        // The id and the region key are joined rather than one standing in
        // for the other: a page whose region keys are its item ids would
        // otherwise collide with a column named after one of them.
        key={`${column.id}:${column.regionKey ?? ""}`}
        // Stacked, a column takes the whole width and the height it needs
        // rather than a share of the panel: `1 1 auto` on both would squeeze
        // every column into an equal slice of the page.
        style={{ flex: "0 0 auto", width: "100%", minWidth: 0, height: "auto" }}
      >
        {column.content}
      </ScrollRegion>
    ))}
  </Focusable>
);
