# Compatibility shim (Phase 4.5 Wave 2, retire per wave-1-decisions.json) --
# imports from the now-installed source_document_extraction package, not
# from a sys.path-injected checkout. Requires source-document-extraction to
# be `pip install -e`'d into whatever environment runs docx-to-content's
# tests during the migration.
from source_document_extraction.dependencies import *  # noqa: F401,F403
from source_document_extraction.dependencies import (  # noqa: F401
    DependencyStatus,
    MissingDependencyError,
    probe_pandoc,
    probe_soffice,
    require_soffice_if_needed,
)
