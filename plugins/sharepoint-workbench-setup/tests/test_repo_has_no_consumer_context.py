"""Purpose:
    Prevent tracked repository content and paths from depending on an original consumer environment.

Key Input Dependencies:
    - Git tracked-file listing
    - Repository file contents and paths, excluding local temp/ and .agents/ data.

test_repo_has_no_consumer_context.py

Background:
    This repository is generic and public: nothing in a tracked file may depend on the site, organization or domain it was first
    used on. The banned terms are stored base64-encoded so that this file does not itself contain them. A match fails the test and
    names the file and line; fix it by using a neutral example (fake host, generic list names) or by moving the content to a
    gitignored location (temp/ or a local config).

Layer: plugins/sharepoint-workbench-setup -- tests (repository guard)

Function Index:
    - decode
    - tracked_files
    - test_no_tracked_file_depends_on_the_original_site_context
    - test_no_tracked_file_or_folder_name_carries_the_original_site_context
"""

import base64
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


# Decode the encoded terms used by the repository-genericity checks.
def decode(items):
    """Decode the encoded terms used by the repository-genericity checks."""
    return [base64.b64decode(x).decode() for x in items]


# matched case-insensitively, as whole words/tokens
BANNED_ANY_CASE = decode([
    "aXRhdQ==", "Y3Ni", "Y21hdA==", "Y2Vpcw==", "c2hlcmlmZg==", "c2hlcmlmZnM=", "Y291cnQ=", "Y291cnRz", "Y3JpbWluYWw=", "amFnLmdvdg==",
    "Z292LmJjLmNh", "YmNnb3Yuc2hhcmVwb2ludC5jb20=", "YmMgZ292", "cGlvXw==", "aWNtXw==", "aWRpcg==", "b3Jkcw==", "aW50cmFuZXQ=", "YmMgZ292ZXJubWVudA==", "YmMtZ292", "Z292ZXJubWVudCBwaWxvdA==", "Z292ZXJubWVudCB2aXNpb24=",
    "Y3Jvd25uZXQ=", "bXlzYw==", "YmNwcw==", "cG9saWNl", "anVkZ2U=", "anVkZ2Vz", "cHJvdGVjdGlvbiBvcmRlcg==", "cHJvdGVjdGlvbiBvcmRlcnM=", "Y2FzZSBtYW5hZ2VtZW50", "cml0bQ==", "c2hlcmlmZg==",
])
# matched exactly as capitalised (the plural words are ordinary English in lower case)
BANNED_CAPITALISED = decode(["UGVyc29ucw==", "TmFycmF0aXZlcw=="])

# false positives that are ordinary English or a substring of an unrelated token, keyed by (path suffix, term)
ALLOWED = {
    ("plugin-sources.json", decode(["YmMtZ292"])[0]),   # an external design-system plugin source listed for the installer; owner decision pending
    ("research-sharepoint-content-creation-and-curation.md", decode(["aW50cmFuZXQ="])[0]),   # the cited external source's own title
    ("verify-agentassets-artifact.ps1", decode(["Y21hdA=="])[0]),   # $descMatch
}


# Return git-tracked repository paths after excluding local-only artifacts.
def tracked_files():
    """Return git-tracked repository paths after excluding local-only artifacts."""
    if shutil.which("git") is None:
        pytest.skip("git not available")
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    return [p for p in out.stdout.split("\0") if p and not p.startswith(("temp/", ".agents/")) and p != "LICENSE"]


# No tracked file content contains a banned consumer-specific term outside the documented allowlist.
def test_no_tracked_file_depends_on_the_original_site_context():
    """No tracked file content contains a banned consumer-specific term outside the documented allowlist."""
    patterns = [(t, re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.IGNORECASE)) for t in BANNED_ANY_CASE]
    patterns += [(t, re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])")) for t in BANNED_CAPITALISED]
    offenders = []
    for rel in tracked_files():
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.split("\n"), 1):
            for term, rx in patterns:
                if rx.search(line) and not any(rel.endswith(suffix) and term == t for suffix, t in ALLOWED):
                    offenders.append(f"{rel}:{number}: {term!r}")
    assert not offenders, "consumer-specific context found:\n" + "\n".join(offenders[:40])


# No tracked file or folder path contains a banned consumer-specific term.
def test_no_tracked_file_or_folder_name_carries_the_original_site_context():
    """No tracked file or folder path contains a banned consumer-specific term."""
    patterns = [re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.IGNORECASE) for t in BANNED_ANY_CASE]
    patterns += [re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])") for t in BANNED_CAPITALISED]
    names = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, text=True).stdout.split("\0")
    offenders = [n for n in names if n and not n.startswith(("temp/", ".agents/")) and any(p.search(n.replace("/", " ").replace("_", " ").replace("-", " ")) for p in patterns)]
    assert not offenders, offenders[:20]
