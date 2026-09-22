"""Reject deployments whose HTML references missing JS or CSS bundles."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class BundleReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.references.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in {"stylesheet", "modulepreload"}:
            self.references.append(attrs.get("href", ""))


def verify(folder):
    folder = Path(folder).resolve()
    parser = BundleReferences()
    parser.feed((folder / "index.html").read_text())
    if not parser.references:
        raise ValueError("Frontend HTML does not reference any bundles")
    for reference in parser.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        asset = (folder / unquote(url.path).lstrip("/")).resolve()
        if not asset.is_relative_to(folder) or not asset.is_file():
            raise ValueError(f"Frontend bundle is missing: {reference}")
    print("Frontend bundle references verified")


if __name__ == "__main__":
    verify(sys.argv[1])
