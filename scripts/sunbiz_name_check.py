#!/usr/bin/env python3
"""Search Sunbiz corporate data files (fixed-width, 1440 chars) for names close to ECFiler.

Usage: python3 -I scripts/sunbiz_name_check.py FILE...
       (FILE = the quarterly cordata.zip, streamed without extracting, or daily yyyymmddc.txt)

The files come from the Division of Corporations' public bulk-data SFTP server,
whose host and public credentials are published on
https://dos.fl.gov/sunbiz/other-services/data-downloads/ (quarterly file:
doc/Quarterly/Cor/cordata.zip, ~1.8 GB; daily files: doc/cor/yyyymmddc.txt).
search.sunbiz.org itself sits behind a bot challenge; this is the sanctioned
bulk route. Result of the 2026-11-13 run: docs/fl/entity-recommendation.md.

Layout (dos.fl.gov corporate-data-file definitions): doc number 1-12, name 13-204,
status 205 (A/I), filing type 206-220, file date 473-480.

Florida treats names as not distinguishable when they differ only by entity
designator, punctuation, spacing, a leading "THE", or "and"/"&". The normalizer
drops those, so a hit on the normalized key is a real conflict candidate.
"""
import io
import re
import subprocess
import sys
import zipfile

SUFFIXES = r"(LIMITED LIABILITY COMPANY|LIMITED COMPANY|L\.?\s?L\.?\s?C\.?|INCORPORATED|INC\.?|CORPORATION|CORP\.?|COMPANY|CO\.?|LTD\.?|P\.?\s?A\.?|L\.?\s?C\.?)$"


def norm(name: str) -> str:
    n = name.upper().strip()
    for _ in range(2):
        n = re.sub(r"[\s,]+" + SUFFIXES, "", n).strip()
    n = re.sub(r"^THE\s+", "", n)
    n = n.replace("&", "AND")
    return re.sub(r"[^A-Z0-9]", "", n)


TARGETS = {"ECFILER", "ECFFILER"}  # "ECFiler", "ECF Filer" (both normalize here)
LOOSE = re.compile(r"E\W*C\W*F\W*-?\W*FIL", re.I)  # anything ECF...FIL, for a near-miss list


def scan(stream, label, stats):
    for raw in stream:
        line = raw.decode("latin-1")
        if len(line) < 205:
            continue
        stats["records"] += 1
        name = line[12:204].strip()
        key = norm(name)
        if key in TARGETS or LOOSE.search(name) or "ECFILER" in key:
            print(f"HIT [{label}] {line[0:12].strip()} | {name} | status={line[204]} | type={line[205:220].strip()} | filed={line[472:480]} | key={key}")
            stats["hits"] += 1


def main() -> None:
    stats = {"records": 0, "hits": 0}
    for path in sys.argv[1:]:
        if path.endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                members = z.infolist()
            for info in members:
                if info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    with zipfile.ZipFile(path) as z, z.open(info) as f:
                        scan(io.BufferedReader(f), info.filename, stats)
                else:
                    # The quarterly cordata.zip uses Deflate64 (method 9), which
                    # Python's zipfile cannot read; Info-ZIP's unzip streams it.
                    proc = subprocess.Popen(["unzip", "-p", path, info.filename], stdout=subprocess.PIPE)
                    scan(proc.stdout, info.filename, stats)
                    if proc.wait() != 0:
                        sys.exit(f"unzip failed on {info.filename}")
                print(f"done {info.filename} ({info.file_size} bytes) records so far {stats['records']}", file=sys.stderr)
        else:
            with open(path, "rb") as f:
                scan(f, path.rsplit("/", 1)[-1], stats)
    print(f"TOTAL records scanned={stats['records']} hits={stats['hits']}")
    for probe in ["ECFiler LLC", "ECFiler", "ECF Filer", "E.C.F. Filer, L.L.C.", "The ECFiler Company", "ECFiler Software LLC"]:
        print(f"normalizer check: {probe!r} -> {norm(probe)}")


if __name__ == "__main__":
    main()
