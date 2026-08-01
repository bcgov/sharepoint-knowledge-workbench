# Compatibility shim (Phase 4.5 Wave 2, retire per wave-1-decisions.json) --
# imports from the now-installed source_document_extraction package.
from source_document_extraction.pandoc_fixes.toc import *  # noqa: F401,F403
from source_document_extraction.pandoc_fixes.toc import (  # noqa: F401
    _BOOKMARK_ANCHOR_LINE,
    _TOC_LINK_LINE,
    _TOC_SLUG_LINE,
)
