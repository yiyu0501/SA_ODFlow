from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED
from zipfile import ZIP_STORED
from zipfile import ZipFile

from generators.export_utils import prepare_output_path, validate_export_payload


def _paragraph_xml(text: str) -> str:
    return f"<text:p>{escape(text)}</text:p>"


def _build_content_xml(content_json: dict) -> str:
    paragraphs = [
        '<text:h text:outline-level="1">會議紀錄</text:h>',
        _paragraph_xml(f"會議名稱：{content_json['meeting_title']}"),
        _paragraph_xml(f"會議日期：{content_json['meeting_date']}"),
        _paragraph_xml(f"會議時間：{content_json['meeting_time']}"),
        _paragraph_xml(f"會議地點：{content_json['location']}"),
        _paragraph_xml(f"主席：{content_json['chair']}"),
        _paragraph_xml(f"紀錄：{content_json['recorder']}"),
        _paragraph_xml(f"出席人員：{'、'.join(content_json['attendees'])}"),
        _paragraph_xml(f"請假人員：{'、'.join(content_json['absentees'])}"),
        '<text:h text:outline-level="2">討論事項與決議</text:h>',
    ]

    for index, item in enumerate(content_json["agenda_items"], start=1):
        paragraphs.extend(
            [
                _paragraph_xml(f"{index}. 議題：{item['title']}"),
                _paragraph_xml(f"討論：{item['discussion']}"),
                _paragraph_xml(f"決議：{item['decision']}"),
            ]
        )

    paragraphs.append('<text:h text:outline-level="2">待辦事項</text:h>')
    for index, item in enumerate(content_json["action_items"], start=1):
        paragraphs.append(
            _paragraph_xml(
                f"{index}. 待辦：{item['task']}／負責人：{item['owner']}／期限：{item['deadline']}／備註：{item['note']}"
            )
        )

    paragraphs.extend(
        [
            _paragraph_xml(f"下次會議時間：{content_json['next_meeting_time']}"),
            _paragraph_xml(f"備註：{content_json['notes']}"),
        ]
    )

    body = "\n".join(paragraphs)
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


def generate_meeting_minutes_odt(
    document: dict,
    version: dict,
    output_dir: Path | str | None = None,
) -> Path:
    validated_document, validated_version = validate_export_payload(document, version)
    output_path = prepare_output_path(validated_document, validated_version, "odt", output_dir)
    content_xml = _build_content_xml(validated_version["content_json"])
    odt_files = _minimal_odt_files(content_xml)

    with ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", odt_files["mimetype"], compress_type=ZIP_STORED)
        for path, file_content in odt_files.items():
            if path == "mimetype":
                continue
            archive.writestr(path, file_content, compress_type=ZIP_DEFLATED)

    return output_path
