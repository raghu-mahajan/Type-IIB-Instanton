# Type IIB Instanton Notes

This repository contains notes on flat-space worldsheet conventions for Type IIB string theory. The current chapter records the free-boson, free-fermion, ghost, superconformal, BRST, and picture-changing conventions used in subsequent calculations.

- [Read the HTML notes](https://raghu-mahajan.github.io/Type-IIB-Instanton/)
- [Download the PDF](https://raghu-mahajan.github.io/Type-IIB-Instanton/type_iib_worldsheet_conventions.pdf)
- [Edit the LaTeX source](Notes/type_iib_worldsheet_conventions.tex)

The formulas are grounded principally in arXiv:2606.06596, with the ten-dimensional gamma-matrix and spin-field conventions taken from arXiv:2110.06949.

## Build

From the repository root, run:

```sh
sh Notes/build_site.sh
```

The script builds the PDF, converts the LaTeX source with LaTeXML, and assembles the static site under `docs/`.
