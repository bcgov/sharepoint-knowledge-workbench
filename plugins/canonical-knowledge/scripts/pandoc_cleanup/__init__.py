# pandoc_cleanup/ -- plugin-local copy of source-document-extraction's
# pandoc/ cleanup family (attrs, footnotes, heading_emphasis, images,
# tables, toc, validate). canonical-knowledge's convert.py independently
# re-extracts and re-cleans the source document (a second, separate pandoc
# pass from source-document-extraction's analysis-time extraction) to
# build canonical content -- it cannot depend on source-document-
# extraction's installed package at runtime (cross-plugin dependency
# prohibited). Named `pandoc_cleanup` rather than `pandoc` to avoid
# colliding with source-document-extraction's own bare `pandoc` package
# once both are pip install -e'd together in docx-to-content's
# compatibility-shim environment. Kept in sync by hand with the producer's
# copy -- see
# docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md.
