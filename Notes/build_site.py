from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re
import shutil
import stat
import subprocess

from build_html import render_article


NOTES_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = NOTES_DIR.parent
BUILD_DIR = NOTES_DIR / "build"
DOCS_DIR = REPOSITORY_DIR / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
PDF_DIR = REPOSITORY_DIR / "output" / "pdf"
MANIFEST_PATH = NOTES_DIR / "documents.json"

LATEXML_CSS_DIR = Path(
    "/opt/local/lib/perl5/vendor_perl/5.34/LaTeXML/resources/CSS"
)


def run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def load_manifest() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    documents = manifest.get("documents", [])
    if not documents:
        raise ValueError("documents.json must contain at least one document")

    bibliography_style = manifest["bibliography_style"]["name"]
    slugs: set[str] = set()
    for document in documents:
        slug = document["slug"]
        if slug in slugs:
            raise ValueError(f"Duplicate document slug: {slug}")
        if not slug or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-"
            for character in slug
        ):
            raise ValueError(
                f"Document slug {slug!r} may contain only lowercase letters, numbers, and hyphens"
            )
        slugs.add(slug)

        source = NOTES_DIR / document["source"]
        if not source.is_file():
            raise FileNotFoundError(f"Document source does not exist: {source}")
        source_text = source.read_text(encoding="utf-8")
        expected_style_command = f"\\bibliographystyle{{{bibliography_style}}}"
        if "\\bibliography{" in source_text and expected_style_command not in source_text:
            raise ValueError(
                f"{source.name} must use \\bibliographystyle{{{bibliography_style}}}"
            )

    return manifest


def sync_bibliography_style(manifest: dict) -> None:
    style = manifest["bibliography_style"]
    template_file = Path(style["template_file"])
    repository_file = NOTES_DIR / style["repository_file"]

    if template_file.is_file():
        shutil.copyfile(template_file, repository_file)
        repository_file.chmod(0o644)
    elif not repository_file.is_file():
        raise FileNotFoundError(
            "The bibliography style is missing from both the LaTeX template "
            f"and the repository: {style['name']}"
        )


def remove_loose_build_artifacts(source: Path) -> None:
    for suffix in (
        ".aux",
        ".bbl",
        ".blg",
        ".fdb_latexmk",
        ".fls",
        ".log",
        ".out",
        ".pdf",
        ".synctex.gz",
        ".toc",
        ".xml",
        ".latexml.log",
        ".latexmlpost.log",
    ):
        (source.parent / f"{source.stem}{suffix}").unlink(missing_ok=True)


def prepare_html_source(source: Path, built_bbl: Path, build_dir: Path) -> Path:
    source_text = source.read_text(encoding="utf-8")
    bibliography_commands = re.compile(
        r"\\bibliographystyle\{[^}]+\}\s*\\bibliography\{[^}]+\}"
    )
    if not bibliography_commands.search(source_text):
        return source

    html_source = build_dir / f"{source.stem}_html.tex"
    bbl_input = f"\\input{{{built_bbl.name}}}"
    html_source.write_text(
        bibliography_commands.sub(
            lambda _match: bbl_input, source_text, count=1
        ),
        encoding="utf-8",
    )
    return html_source


def copy_shared_assets() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for filename in ("LaTeXML.css", "ltx-article.css"):
        destination = ASSETS_DIR / filename
        if destination.exists():
            destination.chmod(destination.stat().st_mode | stat.S_IWUSR)
        shutil.copy2(LATEXML_CSS_DIR / filename, destination)
        destination.chmod(destination.stat().st_mode | stat.S_IWUSR)


def build_document(document: dict) -> None:
    slug = document["slug"]
    source = NOTES_DIR / document["source"]
    document_build_dir = BUILD_DIR / slug
    document_output_dir = DOCS_DIR / slug
    document_build_dir.mkdir(parents=True, exist_ok=True)
    document_output_dir.mkdir(parents=True, exist_ok=True)

    source_stem = source.stem
    built_pdf = document_build_dir / f"{source_stem}.pdf"
    built_bbl = document_build_dir / f"{source_stem}.bbl"
    built_xml = document_build_dir / f"{source_stem}.xml"
    built_html = document_build_dir / f"{source_stem}.html"
    published_pdf_name = document.get("pdf", f"{slug}.pdf")

    remove_loose_build_artifacts(source)
    run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-outdir={document_build_dir}",
            source.name,
        ],
        cwd=source.parent,
    )
    html_source = prepare_html_source(source, built_bbl, document_build_dir)
    run(
        [
            "latexml",
            f"--path={source.parent}",
            f"--dest={built_xml}",
            html_source.name,
        ],
        cwd=html_source.parent,
    )
    run(
        [
            "latexmlpost",
            f"--dest={built_html}",
            "--format=html5",
            "--navigationtoc=context",
            str(built_xml),
        ],
        cwd=html_source.parent,
    )

    render_article(
        source_html=built_html,
        output_html=document_output_dir / "index.html",
        pdf_name=published_pdf_name,
        description=document["description"],
    )
    shutil.copy2(built_pdf, document_output_dir / published_pdf_name)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_pdf, PDF_DIR / published_pdf_name)
    remove_loose_build_artifacts(source)


def render_catalog(manifest: dict) -> None:
    project_title = escape(manifest["project_title"])
    documents = manifest["documents"]
    count = len(documents)
    count_label = f"{count} document" if count == 1 else f"{count} documents"

    document_links = "\n".join(
        f'''      <li class="document-item">
        <a class="document-link" href="{escape(document["slug"])}/">
          <span>{escape(document["title"])}</span>
          <span class="document-format" aria-hidden="true">HTML&nbsp;↗</span>
        </a>
      </li>'''
        for document in documents
    )

    catalog = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Documents for {project_title}.">
  <title>{project_title}</title>
  <link rel="stylesheet" href="assets/catalog.css">
</head>
<body>
  <main class="catalog-shell">
    <nav class="breadcrumbs" aria-label="Breadcrumb">
      <a href="https://raghu-mahajan.github.io/">Home</a>
      <span aria-hidden="true">/</span>
      <a href="https://raghu-mahajan.github.io/projects/">Projects</a>
      <span aria-hidden="true">/</span>
      <span>Type IIB instantons</span>
    </nav>

    <h1>{project_title}</h1>
    <p class="document-count">{count_label}</p>

    <ul class="document-list">
{document_links}
    </ul>
  </main>
</body>
</html>
'''
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "index.html").write_text(catalog, encoding="utf-8")


def remove_legacy_public_files() -> None:
    for path in (
        DOCS_DIR / "type_iib_worldsheet_conventions.pdf",
        DOCS_DIR / "type_iib_worldsheet_conventions.tex",
        DOCS_DIR / "references.bib",
        DOCS_DIR / "apsrev4-1long.bst",
        PDF_DIR / "type_iib_worldsheet_conventions.pdf",
    ):
        path.unlink(missing_ok=True)


def main() -> None:
    manifest = load_manifest()
    sync_bibliography_style(manifest)
    copy_shared_assets()
    for document in manifest["documents"]:
        build_document(document)
    render_catalog(manifest)
    remove_legacy_public_files()


if __name__ == "__main__":
    main()
