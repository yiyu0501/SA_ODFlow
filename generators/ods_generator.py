from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from generators.document_layout import build_spreadsheet_template_spec
from generators.document_style import BODY_FONT_SIZE_PT, ODF_FONT_FAMILY, TABLE_FONT_SIZE_PT


def _paragraph_xml(value: str, style_name: str = "PBody") -> str:
    return f'<text:p text:style-name="{style_name}">{escape(str(value or ""))}</text:p>'


def _cell_xml(
    value: str,
    cell_style: str = "CellBody",
    paragraph_style: str = "PBody",
    *,
    span: int = 1,
) -> str:
    span_attributes = (
        f' table:number-columns-spanned="{span}"'
        if span > 1
        else ""
    )
    return (
        f'<table:table-cell table:style-name="{cell_style}" office:value-type="string"{span_attributes}>'
        f"{_paragraph_xml(value, paragraph_style)}"
        "</table:table-cell>"
    )


def _covered_cells_xml(count: int) -> str:
    return "<table:covered-table-cell/>" * max(count, 0)


def _row_xml(cells: list[str], style_name: str = "RowDefault") -> str:
    return f'<table:table-row table:style-name="{style_name}">{"".join(cells)}</table:table-row>'


def _column_styles_xml(column_count: int) -> tuple[str, str]:
    styles = []
    columns = []
    for index in range(column_count):
        style_name = f"Co{index + 1}"
        width = "2.1cm" if index == 0 else "3.2cm"
        styles.append(
            f'<style:style style:name="{style_name}" style:family="table-column">'
            f'<style:table-column-properties style:column-width="{width}"/>'
            "</style:style>"
        )
        columns.append(f'<table:table-column table:style-name="{style_name}"/>')
    return "".join(styles), "".join(columns)


def _build_spreadsheet_content_xml(template_definition: dict) -> str:
    spec = build_spreadsheet_template_spec(template_definition)
    column_count = max(int(spec.get("column_count", 1)), 1)
    column_styles_xml, columns_xml = _column_styles_xml(column_count)

    title_row = _row_xml(
        [
            _cell_xml(spec["title"], "CellTitle", "PTitle", span=column_count),
            _covered_cells_xml(column_count - 1),
        ]
    )
    metadata_row = _row_xml(
        [
            _cell_xml(spec["metadata"], "CellMeta", "PMeta", span=column_count),
            _covered_cells_xml(column_count - 1),
        ],
        style_name="RowMeta",
    )
    note_row = _row_xml(
        [
            _cell_xml(f"使用說明：{spec['note']}", "CellNote", "PNote", span=column_count),
            _covered_cells_xml(column_count - 1),
        ]
    )
    spacer_row = _row_xml([_cell_xml("", "CellBlank", "PBody") for _ in range(column_count)])
    header_row = _row_xml(
        [_cell_xml(header, "CellHeader", "PHeader") for header in spec["headers"]],
        style_name="RowHeader",
    )
    blank_rows = [
        _row_xml(
            [_cell_xml("", "CellBody", "PBody") for _ in range(column_count)],
            style_name="RowData",
        )
        for _ in range(spec["blank_rows"])
    ]
    table_name = escape(spec["title"])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    {column_styles_xml}
    <style:style style:name="RowDefault" style:family="table-row">
      <style:table-row-properties style:row-height="0.7cm"/>
    </style:style>
    <style:style style:name="RowMeta" style:family="table-row">
      <style:table-row-properties style:row-height="0.8cm"/>
    </style:style>
    <style:style style:name="RowHeader" style:family="table-row">
      <style:table-row-properties style:row-height="0.75cm"/>
    </style:style>
    <style:style style:name="RowData" style:family="table-row">
      <style:table-row-properties style:row-height="0.72cm"/>
    </style:style>
    <style:style style:name="PTitle" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="16pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PMeta" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PHeader" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PBody" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PNote" style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="10pt"/>
    </style:style>
    <style:style style:name="CellTitle" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #666666" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellMeta" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #666666" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellNote" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #666666" fo:padding="0.12cm"/>
    </style:style>
    <style:style style:name="CellHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #333333" fo:padding="0.1cm" fo:background-color="#d9d9d9"/>
    </style:style>
    <style:style style:name="CellBody" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #555555" fo:padding="0.1cm"/>
    </style:style>
    <style:style style:name="CellBlank" style:family="table-cell">
      <style:table-cell-properties fo:border="none" fo:padding="0.1cm"/>
    </style:style>
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      <table:table table:name="{table_name}">
        {columns_xml}
        {title_row}
        {metadata_row}
        {note_row}
        {spacer_row}
        {header_row}
        {''.join(blank_rows)}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _minimal_ods_files(content_xml: str) -> dict[str, str]:
    return {
        "mimetype": "application/vnd.oasis.opendocument.spreadsheet",
        "content.xml": content_xml,
        "styles.xml": f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:version="1.2">
  <office:styles>
    <style:default-style style:family="paragraph">
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt"/>
    </style:default-style>
  </office:styles>
  <office:automatic-styles/>
  <office:master-styles/>
</office:document-styles>
""",
        "meta.xml": """<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    office:version="1.2">
  <office:meta/>
</office:document-meta>
""",
        "settings.xml": """<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    office:version="1.2">
  <office:settings/>
</office:document-settings>
""",
        "META-INF/manifest.xml": """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
    xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
    manifest:version="1.2">
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.spreadsheet" manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="settings.xml"/>
</manifest:manifest>
""",
    }


def generate_ods_template(
    template_definition: dict,
    output_path: Path | str,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_map = _minimal_ods_files(_build_spreadsheet_content_xml(template_definition))

    with ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", file_map["mimetype"], compress_type=ZIP_STORED)
        for path, file_content in file_map.items():
            if path == "mimetype":
                continue
            archive.writestr(path, file_content, compress_type=ZIP_DEFLATED)

    return output_path
