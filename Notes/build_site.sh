#!/bin/sh
set -eu

cd "$(dirname "$0")"

mkdir -p build ../docs/assets ../output/pdf

latexmk -pdf -interaction=nonstopmode -halt-on-error \
  -outdir=build type_iib_worldsheet_conventions.tex

latexml --dest=build/type_iib_worldsheet_conventions.xml \
  type_iib_worldsheet_conventions.tex

latexmlpost --dest=build/type_iib_worldsheet_conventions.html \
  --format=html5 --navigationtoc=context \
  build/type_iib_worldsheet_conventions.xml

python3 build_html.py

cp build/type_iib_worldsheet_conventions.pdf \
  ../output/pdf/type_iib_worldsheet_conventions.pdf
cp build/type_iib_worldsheet_conventions.pdf \
  ../docs/type_iib_worldsheet_conventions.pdf
cp type_iib_worldsheet_conventions.tex \
  ../docs/type_iib_worldsheet_conventions.tex
cp references.bib ../docs/references.bib
cp apsrev4-1long.bst ../docs/apsrev4-1long.bst
chmod u+w ../docs/assets/LaTeXML.css ../docs/assets/ltx-article.css 2>/dev/null || true
cp /opt/local/lib/perl5/vendor_perl/5.34/LaTeXML/resources/CSS/LaTeXML.css \
  ../docs/assets/LaTeXML.css
cp /opt/local/lib/perl5/vendor_perl/5.34/LaTeXML/resources/CSS/ltx-article.css \
  ../docs/assets/ltx-article.css
chmod u+w ../docs/assets/LaTeXML.css ../docs/assets/ltx-article.css
