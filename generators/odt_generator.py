from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from core.document_schemas import canonical_document_type, derive_document_title
from generators.document_layout import build_document_render_spec, build_template_render_spec
from generators.document_style import (
    BODY_FONT_SIZE_PT,
    NOTE_FONT_SIZE_PT,
    ODF_FONT_FAMILY,
    PAGE_HEIGHT_CM,
    PAGE_MARGIN_CM,
    PAGE_WIDTH_CM,
    SECTION_FONT_SIZE_PT,
    TABLE_FONT_SIZE_PT,
    TITLE_FONT_SIZE_PT,
)
from generators.export_utils import prepare_output_path, validate_export_payload
from generators.template_renderer import TemplateRenderError, render_document_odt_template


def _paragraph_xml(text: str, style_name: str = "PBody") -> str:
    paragraphs = [line.strip() for line in str(text or "").split("\n")] or [""]
    xml_parts = []
    for paragraph in paragraphs:
        xml_parts.append(f'<text:p text:style-name="{style_name}">{escape(paragraph)}</text:p>')
    return "".join(xml_parts)


def _heading_xml(text: str, style_name: str, level: int) -> str:
    return (
        f'<text:h text:style-name="{style_name}" text:outline-level="{level}">'
        f"{escape(text)}</text:h>"
    )


def _cell_xml(text: str, cell_style: str, paragraph_style: str) -> str:
    return (
        f'<table:table-cell table:style-name="{cell_style}" office:value-type="string">'
        f"{_paragraph_xml(text, paragraph_style)}"
        "</table:table-cell>"
    )


def _covered_cell_xml() -> str:
    return "<table:covered-table-cell/>"


def _table_row_xml(row: list[str], cell_styles: list[tuple[str, str]]) -> str:
    cells = [
        _cell_xml(value, cell_style=cell_style, paragraph_style=paragraph_style)
        for value, (cell_style, paragraph_style) in zip(row, cell_styles)
    ]
    return "<table:table-row>" + "".join(cells) + "</table:table-row>"


def _table_xml(
    name: str,
    headers: list[str],
    rows: list[list[str]],
    info_table: bool = False,
) -> str:
    column_count = len(headers) if headers else max((len(row) for row in rows), default=1)
    if column_count <= 2:
        column_style = "CoWide"
    elif column_count <= 4:
        column_style = "CoMedium"
    else:
        column_style = "CoNarrow"
    column_block = "".join(
        f'<table:table-column table:style-name="{column_style}"/>'
        for _ in range(column_count)
    )

    body_rows = []
    if headers:
        header_styles = [("CellHeader", "PTableHeader")] * len(headers)
        body_rows.append(_table_row_xml(headers, header_styles))

    for row in rows:
        if info_table:
            styles = []
            for index in range(len(row)):
                if index % 2 == 0:
                    styles.append(("CellLabel", "PLabel"))
                else:
                    styles.append(("CellValue", "PBody"))
            body_rows.append(_table_row_xml(row, styles))
        else:
            body_rows.append(
                _table_row_xml(row, [("CellBody", "PTableBody")] * len(row))
            )

    return (
        f'<table:table table:name="{escape(name)}" table:style-name="TableBase">'
        f"{column_block}"
        f"{''.join(body_rows)}"
        "</table:table>"
    )


def _render_sections(spec: dict) -> str:
    title_lines = [line.strip() for line in str(spec["title"] or "").split("\n") if line.strip()] or [""]
    body_parts = [_heading_xml(line, "PTitle", level=1) for line in title_lines]

    for section in spec["sections"]:
        kind = section["kind"]
        heading = section.get("heading")
        if heading:
            body_parts.append(_heading_xml(heading, "PSection", level=2))

        if kind == "info_table":
            rows = section["rows"]
            body_parts.append(_table_xml(heading or "基本資料", [], rows, info_table=True))
        elif kind == "paragraph":
            for paragraph in section["paragraphs"]:
                body_parts.append(_paragraph_xml(paragraph, "PBody"))
        elif kind == "bullet_list":
            items = "".join(
                f"<text:list-item>{_paragraph_xml(item, 'PBody')}</text:list-item>"
                for item in section["items"]
            )
            body_parts.append(f'<text:list text:style-name="ListDefault">{items}</text:list>')
        elif kind == "lines":
            for line in section["lines"]:
                body_parts.append(_paragraph_xml(line, "PBody"))
        elif kind == "table":
            body_parts.append(_table_xml(heading or "表格", section["headers"], section["rows"]))
        elif kind == "note":
            body_parts.append(_paragraph_xml(section["text"], "PNote"))

    return "\n".join(body_parts)


def _wrap_text_document(body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles>
    <style:style style:name="PBody" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0.14cm" fo:line-height="130%"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PTitle" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0.35cm"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TITLE_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PSection" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0.28cm" fo:margin-bottom="0.14cm"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{SECTION_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PLabel" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PTableHeader" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center" fo:margin-top="0cm" fo:margin-bottom="0cm"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="PTableBody" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0cm"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{TABLE_FONT_SIZE_PT}pt"/>
    </style:style>
    <style:style style:name="PNote" style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0.08cm" fo:margin-bottom="0.08cm"/>
      <style:text-properties fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{NOTE_FONT_SIZE_PT}pt"/>
    </style:style>
    <text:list-style style:name="ListDefault">
      <text:list-level-style-bullet text:level="1" text:bullet-char="•">
        <style:list-level-properties text:space-before="0.5cm" text:min-label-width="0.35cm"/>
      </text:list-level-style-bullet>
    </text:list-style>
    <style:style style:name="TableBase" style:family="table">
      <style:table-properties table:border-model="collapsing"/>
    </style:style>
    <style:style style:name="CoWide" style:family="table-column">
      <style:table-column-properties style:column-width="4.8cm"/>
    </style:style>
    <style:style style:name="CoMedium" style:family="table-column">
      <style:table-column-properties style:column-width="3.3cm"/>
    </style:style>
    <style:style style:name="CoNarrow" style:family="table-column">
      <style:table-column-properties style:column-width="2.6cm"/>
    </style:style>
    <style:style style:name="CellLabel" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #333333" fo:padding="0.08cm" fo:background-color="#efefef"/>
    </style:style>
    <style:style style:name="CellValue" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #333333" fo:padding="0.08cm"/>
    </style:style>
    <style:style style:name="CellHeader" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #333333" fo:padding="0.08cm" fo:background-color="#d9d9d9"/>
    </style:style>
    <style:style style:name="CellBody" style:family="table-cell">
      <style:table-cell-properties fo:border="0.03cm solid #333333" fo:padding="0.08cm"/>
    </style:style>
  </office:automatic-styles>
  <office:body>
    <office:text>
      {body}
    </office:text>
  </office:body>
</office:document-content>
"""


def _minimal_odt_files(content_xml: str) -> dict[str, str]:
    return {
        "mimetype": "application/vnd.oasis.opendocument.text",
        "content.xml": content_xml,
        "styles.xml": f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    office:version="1.2">
  <office:font-face-decls>
    <style:font-face style:name="FormalCJK" svg:font-family="{escape(ODF_FONT_FAMILY)}"/>
  </office:font-face-decls>
  <office:styles>
    <style:default-style style:family="paragraph">
      <style:text-properties style:font-name="FormalCJK" fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="{BODY_FONT_SIZE_PT}pt"/>
    </style:default-style>
    <style:style style:name="Footer" style:family="paragraph">
      <style:paragraph-properties fo:text-align="center"/>
      <style:text-properties style:font-name="FormalCJK" fo:font-family="{escape(ODF_FONT_FAMILY)}" fo:font-size="10pt"/>
    </style:style>
  </office:styles>
  <office:automatic-styles>
    <style:page-layout style:name="pm1">
      <style:page-layout-properties fo:page-width="{PAGE_WIDTH_CM}" fo:page-height="{PAGE_HEIGHT_CM}" style:print-orientation="portrait" fo:margin-top="{PAGE_MARGIN_CM}" fo:margin-bottom="{PAGE_MARGIN_CM}" fo:margin-left="{PAGE_MARGIN_CM}" fo:margin-right="{PAGE_MARGIN_CM}"/>
    </style:page-layout>
  </office:automatic-styles>
  <office:master-styles>
    <style:master-page style:name="Standard" style:page-layout-name="pm1">
      <style:footer>
        <text:p text:style-name="Footer">第<text:page-number text:select-page="current">1</text:page-number>頁　共<text:page-count>1</text:page-count>頁</text:p>
      </style:footer>
    </style:master-page>
  </office:master-styles>
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
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="settings.xml"/>
</manifest:manifest>
""",
    }


def _write_odf_package(output_path: Path, file_map: dict[str, str]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", file_map["mimetype"], compress_type=ZIP_STORED)
        for path, file_content in file_map.items():
            if path == "mimetype":
                continue
            archive.writestr(path, file_content, compress_type=ZIP_DEFLATED)
    return output_path


def generate_document_odt(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    validated_document, validated_version = validate_export_payload(document, version)
    output_path = prepare_output_path(validated_document, validated_version, "odt", output_dir)
    canonical_type = canonical_document_type(validated_document["document_type"])
    template_document = {**validated_document, "document_type": canonical_type}

    try:
        template_output = render_document_odt_template(
            canonical_type,
            template_document,
            validated_version["content_json"],
            output_path,
        )
    except TemplateRenderError:
        template_output = None
    if template_output is not None:
        return template_output

    spec = build_document_render_spec(
        canonical_type,
        validated_version["content_json"],
        title_override=derive_document_title(
            canonical_type,
            validated_version["content_json"],
            fallback=validated_document.get("title"),
        ),
    )
    content_xml = _wrap_text_document(_render_sections(spec))
    return _write_odf_package(output_path, _minimal_odt_files(content_xml))


def generate_meeting_minutes_odt(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    return generate_document_odt(document=document, version=version, output_dir=output_dir)


def generate_odt_template(
    template_definition: dict,
    output_path: Path | str,
) -> Path:
    spec = build_template_render_spec(template_definition)
    content_xml = _wrap_text_document(_render_sections(spec))
    return _write_odf_package(Path(output_path), _minimal_odt_files(content_xml))
