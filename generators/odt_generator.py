from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED
from zipfile import ZIP_STORED
from zipfile import ZipFile

from core.document_schemas import build_document_preview_blocks, derive_document_title
from generators.export_utils import prepare_output_path, validate_export_payload


def _paragraph_xml(text: str) -> str:
    return f"<text:p>{escape(text)}</text:p>"


def _heading_xml(text: str, level: int = 1) -> str:
    return f'<text:h text:outline-level="{level}">{escape(text)}</text:h>'


def _list_xml(items: list[str]) -> str:
    list_items = "".join(
        f"<text:list-item><text:p>{escape(item)}</text:p></text:list-item>"
        for item in items
    )
    return f"<text:list>{list_items}</text:list>"


def _build_document_content_xml(document: dict, content_json: dict) -> str:
    blocks = build_document_preview_blocks(
        document["document_type"],
        content_json,
        title_override=derive_document_title(
            document["document_type"],
            content_json,
            fallback=document.get("title"),
        ),
    )
    body_parts = []
    for block in blocks:
        kind = block["kind"]
        if kind == "title":
            body_parts.append(_heading_xml(block["text"], level=1))
        elif kind == "heading":
            body_parts.append(_heading_xml(block["text"], level=block.get("level", 2)))
        elif kind == "paragraph":
            body_parts.append(_paragraph_xml(block["text"]))
        elif kind == "bullet_list":
            body_parts.append(_list_xml(block["items"]))
    return _wrap_text_document("\n".join(body_parts))


def _build_template_content_xml(template_definition: dict) -> str:
    body_parts = [
        _heading_xml(template_definition["name"], level=1),
        _paragraph_xml(f"範本類型：{template_definition['template_type']}"),
        _paragraph_xml(f"建議格式：{template_definition['suggested_format']}"),
        _paragraph_xml(
            "對應評鑑分類："
            + (template_definition.get("evaluation_category") or "未指定")
        ),
        _heading_xml("使用情境", level=2),
        _paragraph_xml(template_definition["usage_description"]),
        _heading_xml("基本欄位", level=2),
    ]

    basic_fields = [f"{field}：________________" for field in template_definition["basic_fields"]]
    body_parts.append(_list_xml(basic_fields))

    body_parts.append(_heading_xml("範本內容", level=2))
    outline_fields = template_definition.get("outline_fields") or []
    if outline_fields:
        body_parts.append(_list_xml([f"{item}：" for item in outline_fields]))

    body_parts.append(_heading_xml("使用說明", level=2))
    body_parts.append(_list_xml(template_definition["instructions"]))

    return _wrap_text_document("\n".join(body_parts))


def _wrap_text_document(body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:version="1.2">
  <office:scripts/>
  <office:automatic-styles/>
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
        "styles.xml": """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
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
    content_xml = _build_document_content_xml(
        validated_document,
        validated_version["content_json"],
    )
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
    content_xml = _build_template_content_xml(template_definition)
    return _write_odf_package(Path(output_path), _minimal_odt_files(content_xml))
