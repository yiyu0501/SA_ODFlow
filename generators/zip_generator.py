from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from core.database import DATA_DIR
from core.filename import sanitize_filename_component


DEFAULT_EXPORT_DIR = DATA_DIR / "generated" / "exports"


def create_package_workspace(root_folder_name: str) -> tuple[Path, Path]:
    workspace_dir = Path(tempfile.mkdtemp(prefix="odflow_export_"))
    package_root = workspace_dir / sanitize_filename_component(
        root_folder_name,
        fallback="evaluation_package",
    )
    package_root.mkdir(parents=True, exist_ok=True)
    return workspace_dir, package_root


def ensure_category_folders(
    package_root: Path,
    categories: list[str],
) -> list[Path]:
    created_paths = []
    for category in categories:
        category_path = package_root / sanitize_filename_component(category, fallback="category")
        category_path.mkdir(parents=True, exist_ok=True)
        created_paths.append(category_path)
    return created_paths


def copy_file_to_category(
    source_path: Path | str,
    package_root: Path,
    category_name: str,
) -> Path:
    source = Path(source_path)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"找不到來源檔案：{source}")

    category_path = package_root / sanitize_filename_component(category_name, fallback="category")
    category_path.mkdir(parents=True, exist_ok=True)

    safe_stem = sanitize_filename_component(source.stem, fallback="document")
    destination = _deduplicate_path(category_path / f"{safe_stem}{source.suffix}")
    shutil.copy2(source, destination)
    return destination


def create_zip_archive(
    package_root: Path,
    zip_name: str,
    output_dir: Path | str | None = None,
) -> Path:
    output_dir_path = Path(output_dir) if output_dir is not None else DEFAULT_EXPORT_DIR
    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_path = _deduplicate_path(output_dir_path / sanitize_filename_component(zip_name, fallback="package.zip"))
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_root.rglob("*")):
            archive.write(path, arcname=path.relative_to(package_root.parent))
    return output_path


def _deduplicate_path(path: Path) -> Path:
    if not path.exists():
        return path

    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1
