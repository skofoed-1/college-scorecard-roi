#!/usr/bin/env python3
"""Downloads the current College Scorecard institution-level bulk data
(a ~96MB CSV once unzipped) and extracts it to data/raw/. No API key or
auth required; the download URL is scraped from the data page since it
includes a date stamp that changes with each data refresh.
"""
import io
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

USER_AGENT = "college-scorecard-roi (contact: kapoc1@gmail.com)"
DATA_PAGE = "https://collegescorecard.ed.gov/data/"

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"


def find_institution_zip_url() -> str:
    req = urllib.request.Request(DATA_PAGE, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")
    match = re.search(r"https://\S+Most-Recent-Cohorts-Institution_\d+\.zip", html)
    if not match:
        sys.exit("Could not find the institution data zip URL on the data page.")
    return match.group(0)


def main() -> None:
    zip_url = find_institution_zip_url()
    print(f"Downloading {zip_url}")

    req = urllib.request.Request(zip_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        zip_bytes = resp.read()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_names = [
            n for n in zf.namelist()
            if n.endswith(".csv") and not Path(n).name.startswith(("._", "__MACOSX"))
        ]
        for name in csv_names:
            target = RAW_DIR / Path(name).name
            target.write_bytes(zf.read(name))
            print(f"Extracted {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
