#!/usr/bin/env python
"""Overlay ECFiler answers onto the flat FL TPV Application (rev. 01-01-2021).

Source form has zero widgets; every insertion is positioned from measured
label/rule geometry (see git history / packet checklist for the fact sheet).
Company name, signatures, dates, and titles are deliberately left blank.
"""
import fitz

SRC = "docs/fl/sources/Third_Party_Vendor_Application_01-01-2021.pdf"
OUT = "docs/fl/Third_Party_Vendor_Application_FILLED.pdf"

BLACK = (0, 0, 0)
GRAY = (0.45, 0.45, 0.45)
F = "helv"
FB = "hebo"  # Helvetica-Bold
font = fitz.Font(F)


def put(page, x, y, text, size=9.5, color=BLACK, fontname=F):
    page.insert_text((x, y), text, fontsize=size, fontname=fontname, color=color)
    return x + fitz.Font(fontname).text_length(text, size)


doc = fitz.open(SRC)

# ---------------- Page 1: Applicant Contact Information -------------------
p = doc[0]
# table: label col1 36-119, value col 120-304 | label col2 305-390, value 391-570
# row1 y 182.2-193.4 (Applicant Name / Contact Email), row2 y 201.4-212.6
put(p, 395, 191.0, "realjacksons@gmail.com")           # Contact Email
put(p, 124.5, 210.2, "Jackson Sanger")                  # Contact Name
put(p, 395, 210.2, "[phone]", color=GRAY)               # Contact Phone
# Applicant Name value cell intentionally blank (entity not yet formed).

# ---------------- Page 3: callback table + Filing Paths grid ---------------
p = doc[2]
# NotifyFilingReviewComplete answer row: y 270.7-288.3
# cols: 49.7-137.8 | 137.8-278.8 | 278.8-486.2 | 486.2-561.5
for x in (55.5, 143.5, 284.5, 492.0):
    put(p, x, 283.0, "N/A", size=9)
put(p, 49.7, 297.8,
    "Not applicable: Applicant will use the FilingReviewCompleteResult "
    "polling service for status retrieval (see cover letter).",
    size=8, color=BLACK)

# Filing Paths grid: cols 36 | 136.2 | 288.4 | 410.9 | 487.8 | 575.2
# "Pleading on Existing Case" column spans x 288.4-410.9 (center 349.65)
# Circuit Civil (CA) row y 491.7-506.9; County Civil (CC) row y 507.7-522.9
xw = fitz.Font(FB).text_length("X", 10)
xc = 349.65 - xw / 2
put(p, xc, 503.5, "X", size=10, fontname=FB)            # CA / Existing Case
put(p, xc, 519.5, "X", size=10, fontname=FB)            # CC / Existing Case

# ---------------- Page 5: Eligibility / company disclosure -----------------
p = doc[4]
# I. Contact Information (labels end: Name 122.6, Address 133.0, Phone 123.5,
# E-mail 124.3; row baselines ~ y1 - 2.5)
put(p, 128.5, 120.2, "Jackson Sanger")
x = put(p, 139.0, 134.5, "[street address]", color=GRAY)
put(p, x + 3, 134.5, "Tampa, FL")
put(p, 129.5, 148.2, "[phone]", color=GRAY)
put(p, 130.5, 161.8, "realjacksons@gmail.com")

# II. Status of Company — margin note (form offers only Corporation /
# Partnership / Joint Venture; do not force the LLC into those boxes).
put(p, 200, 190.2,
    "Applicant will be a single-member Florida limited liability company;",
    size=8)
x = put(p, 200, 200.2, "state and date of organization: Florida, ", size=8)
put(p, x, 200.2, "[date of formation]", size=8, color=GRAY)

# III. Corporate History
put(p, 352.5, 451.5, "[to complete at formation]", size=9, color=GRAY)  # A.
put(p, 322.5, 465.1, "None.")                                            # B.
# C. wraps to the full right margin ("...past five (5) years." ends x=570.9);
# answer goes in the left margin beside the item letter, same baseline.
put(p, 58.0, 479.5, "None.")                                             # C.
put(p, 538.5, 493.1, "No.")                                              # D.
put(p, 194.0, 520.6, "No.")                                              # E.
put(p, 440.5, 534.7, "See attached reference sheet.", size=8.5)          # F.

# Declaration block (Company Name / date / Signature / Title): left blank.

doc.save(OUT)
print("wrote", OUT)
