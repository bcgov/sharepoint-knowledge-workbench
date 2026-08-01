# Compatibility shim (Phase 4.5 Wave 2, retire per wave-1-decisions.json) --
# imports from the now-installed source_document_extraction package.
from source_document_extraction.path_safety import *  # noqa: F401,F403
from source_document_extraction.path_safety import (  # noqa: F401
    EXTERNAL_PREFIXES,
    VIOLATION_ABSOLUTE,
    VIOLATION_TRAVERSAL,
)
