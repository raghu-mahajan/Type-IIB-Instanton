from pathlib import Path
import re


NOTES_DIR = Path(__file__).resolve().parent
REPOSITORY_DIR = NOTES_DIR.parent
SOURCE_HTML = NOTES_DIR / "build" / "type_iib_worldsheet_conventions.html"
OUTPUT_DIR = REPOSITORY_DIR / "docs"
OUTPUT_HTML = OUTPUT_DIR / "index.html"


html = SOURCE_HTML.read_text(encoding="utf-8")

html = html.replace(
    '<link rel="stylesheet" href="LaTeXML.css" type="text/css">\n'
    '<link rel="stylesheet" href="ltx-article.css" type="text/css">',
    '<link rel="stylesheet" href="assets/LaTeXML.css" type="text/css">\n'
    '<link rel="stylesheet" href="assets/ltx-article.css" type="text/css">\n'
    '<link rel="stylesheet" href="assets/site.css" type="text/css">',
)

html = html.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="description" content="Worldsheet conventions for flat ten-dimensional Type IIB string theory, including free fields, ghosts, spin fields, BRST, and picture changing.">',
)

site_header = """<header class="site-header">
  <a class="site-brand" href="./" aria-label="Type IIB Instanton Notes home">
    <span class="site-mark" aria-hidden="true"></span>
    <span>Type IIB Instanton Notes</span>
  </a>
  <nav class="site-links" aria-label="Document links">
    <a href="type_iib_worldsheet_conventions.pdf">PDF</a>
    <a href="type_iib_worldsheet_conventions.tex">TeX source</a>
    <a href="https://arxiv.org/abs/2606.06596">arXiv:2606.06596</a>
    <a href="https://arxiv.org/abs/2110.06949">arXiv:2110.06949</a>
  </nav>
</header>"""

html = html.replace("<body>", "<body>\n" + site_header, 1)

html = html.replace(
    '<nav class="ltx_page_navbar">\n<nav class="ltx_TOC">',
    '<aside class="contents-rail" aria-label="Article contents">\n'
    '  <div class="contents-label">Contents</div>\n'
    '  <nav class="ltx_TOC">',
    1,
)

html = html.replace(
    '</nav>\n</nav>\n<div class="ltx_page_main">',
    '</nav>\n</aside>\n<main class="article-shell">\n'
    '<div class="ltx_page_main">',
    1,
)

actions = """<div class="article-actions" aria-label="Downloads">
  <a class="primary-action" href="type_iib_worldsheet_conventions.pdf">Read the PDF</a>
  <a href="type_iib_worldsheet_conventions.tex">Download the TeX source</a>
</div>"""

html = re.sub(
    r'(<div class="ltx_dates">.*?</div>)',
    r"\1\n" + actions,
    html,
    count=1,
    flags=re.DOTALL,
)

footer = """<footer class="site-footer">
  Generated from the LaTeX source with LaTeXML. Source conventions are linked in the bibliography.
</footer>"""

html = html.replace("</body>", "</main>\n" + footer + "\n</body>", 1)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_HTML.write_text(html, encoding="utf-8")

