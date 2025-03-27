import html

def table_to_html(table) -> str:
    """
    Convert a table object into HTML representation. 
    Designed to work with any table-like structure, not tied to Azure.

    Args:
        table: Table-like object with properties like row_index, column_index, etc.

    Returns:
        str: HTML string of the table.
    """
    table_html = "<table>"
    rows = [
        sorted(
            [cell for cell in table.cells if cell.row_index == i],
            key=lambda cell: cell.column_index
        )
        for i in range(table.row_count)
    ]
    for row_cells in rows:
        table_html += "<tr>"
        for cell in row_cells:
            tag = "th" if cell.kind in ["columnHeader", "rowHeader"] else "td"
            cell_spans = ""
            if cell.column_span > 1:
                cell_spans += f" colSpan={cell.column_span}"
            if cell.row_span > 1:
                cell_spans += f" rowSpan={cell.row_span}"
            table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
        table_html += "</tr>"
    table_html += "</table>"
    return table_html
