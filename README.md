# Type IIB Instanton Notes

This repository collects documents for the Instantons in Type IIB String Theory project. Each LaTeX source is published as an HTML article and a PDF.

- [Browse the documents](https://raghu-mahajan.github.io/Type-IIB-Instanton/)
- [Read Worldsheet Conventions for Type IIB String Theory](https://raghu-mahajan.github.io/Type-IIB-Instanton/worldsheet-conventions/)
- [Download its PDF](https://raghu-mahajan.github.io/Type-IIB-Instanton/worldsheet-conventions/worldsheet-conventions.pdf)
- [Edit the LaTeX source](Notes/type_iib_worldsheet_conventions.tex)

The formulas are grounded principally in arXiv:2606.06596, with the ten-dimensional gamma-matrix and spin-field conventions taken from arXiv:2110.06949.

## Build

From the repository root, run:

```sh
sh Notes/build_site.sh
```

The script reads `Notes/documents.json`, builds every listed source, converts each source with LaTeXML, publishes each article under `docs/<slug>/`, and regenerates the document catalog at `docs/index.html`.

To publish another document, add its `.tex` source under `Notes/` and add one entry to `Notes/documents.json`.

The bibliography style is the vendored `Notes/apsrev4-1long.bst` from `/Users/rm89/Dropbox/RM_Latex_Template`. When that template file is available, the build refreshes the repository copy from it. BibTeX generates the `.bbl` used by both the PDF and the HTML article so that both formats share the same reference style.
