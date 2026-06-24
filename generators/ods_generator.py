from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED
from zipfile import ZIP_STORED
from zipfile import ZipFile


def _cell_xml(value: str) -> str:
    return (
        '<table:table-cell office:value-type="string">'
        f"<text:p>{escape(value)}</text:p>"
        "</table:table-cell>"
    )


def _row_xml(values: list[str]) -> str:
    return "<table:table-row>" + "".join(_cell_xml(value) for value in values) + "</table:table-row>"


def _build_spreadsheet_content_xml(template_definition: dict) -> str:
    basic_rows = [
        ["範本名稱", template_definition["name"]],
        ["範本類型", template_definition["template_type"]],
        ["建議格式", template_definition["suggested_format"]],
        ["對應評鑑分類", template_definition.get("evaluation_category") or "未指定"],
        ["使用情境", template_definition["usage_description"]],
    ]
    instruction_rows = [["使用說明", "；".join(template_definition["instructions"])]]
    header_row = template_definition["table_headers"]
    empty_rows = [["" for _ in header_row] for _ in range(5)]

    table_rows = (
        [_row_xml(row) for row in basic_rows]
        + [_row_xml(["", ""])]
        + [_row_xml(instruction_rows[0])]
        + [_row_xml(["" for _ in header_row])]
        + [_row_xml(header_row)]
        + [_row_xml(row) for row in empty_rows]
    )
    table_name = escape(template_definition["name"])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles/>
  <office:body>
    <office:spreadsheet>
      <table:table table:name="{table_name}">
        {''.join(table_rows)}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>
"""


def _minimal_ods_files(content_xml: str) -> dict[str, str]:
    return {
        "mimetype": "application/vnd.oasis.opendocument.spreadsheet",
        "content.xml": content_xml,
        "styles.xml": """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    office:version="1.2">
  <office:styles/>
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
