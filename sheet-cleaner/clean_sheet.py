"""Clean a messy orders spreadsheet.

Usage:  python clean_sheet.py messy_orders.xlsx cleaned_orders.xlsx

What it does (and writes into a 'report' sheet so nothing changes silently):
  - normalises column names
  - trims and fixes name capitalisation
  - standardises country names, product names
  - parses dates in mixed formats into YYYY-MM-DD (slash dates are read day/month/year)
  - turns "$12.50", "12.50 USD", "12,50" into numbers
  - standardises phone numbers (10 digits -> +1 XXX XXX XXXX)
  - flags invalid or missing emails and quantities instead of guessing
  - removes empty rows and duplicate orders (same order ID, case-insensitive)
"""
import re
import sys
from datetime import datetime

import pandas as pd

COUNTRY_MAP = {
    "usa": "United States", "u.s.a.": "United States", "united states": "United States",
    "uk": "United Kingdom", "united kingdom": "United Kingdom",
    "germany": "Germany", "deutschland": "Germany",
    "canada": "Canada",
}
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y", "%d.%m.%y", "%Y/%m/%d"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_columns(cols):
    return [re.sub(r"\s+", "_", str(c).strip().lower()) for c in cols]


def parse_date(v):
    s = str(v).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_money(v):
    s = str(v).strip().upper().replace("USD", "").replace("$", "").strip()
    if not s:
        return None
    if re.fullmatch(r"\d+,\d{2}", s):  # 12,50 -> 12.50
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def clean_phone(v):
    digits = re.sub(r"\D", "", str(v))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return "+1 %s %s %s" % (digits[:3], digits[3:6], digits[6:])
    return None


def parse_qty(v):
    try:
        q = int(float(str(v).strip()))
        return q if q > 0 else None
    except ValueError:
        return None


def main(src, dst):
    raw = pd.read_excel(src, dtype=str).fillna("")
    raw.columns = clean_columns(raw.columns)
    report = []
    n0 = len(raw)

    # empty rows
    blank = raw.apply(lambda r: all(str(x).strip() == "" for x in r), axis=1)
    raw = raw[~blank].copy()
    report.append(("Empty rows removed", int(blank.sum())))

    df = raw.copy()
    df["order_id"] = df["order_id"].str.strip().str.upper()
    # duplicates
    dup = df.duplicated(subset=["order_id"], keep="first")
    report.append(("Duplicate orders removed (same order ID)", int(dup.sum())))
    df = df[~dup].copy()

    df["customer_name"] = df["customer_name"].str.strip().str.replace(r"\s+", " ", regex=True).str.title()
    df["email"] = df["email"].str.strip().str.lower()
    bad_email = ~df["email"].apply(lambda e: bool(EMAIL_RE.match(e)))
    df["email_issue"] = bad_email.map({True: "missing or invalid", False: ""})
    report.append(("Rows with missing or invalid email (flagged, not changed)", int(bad_email.sum())))

    df["phone"] = df["phone"].apply(clean_phone)
    df["country"] = df["country"].str.strip().str.lower().map(COUNTRY_MAP).fillna(df["country"].str.strip())
    df["product"] = df["product"].str.strip().str.title()

    qty = df["qty"].apply(parse_qty)
    df["qty_issue"] = qty.isna().map({True: "missing or invalid", False: ""})
    report.append(("Rows with missing or invalid quantity (flagged)", int(qty.isna().sum())))
    df["qty"] = qty.astype("Int64")

    df["unit_price_usd"] = df["unit_price"].apply(parse_money)
    df = df.drop(columns=["unit_price"])
    df["order_date"] = df["order_date"].apply(parse_date)
    report.append(("Dates that could not be parsed", int(df["order_date"].isna().sum())))
    df["line_total_usd"] = (df["qty"].astype("float64") * df["unit_price_usd"]).round(2)

    df = df.sort_values("order_id")
    report.insert(0, ("Rows in input file", n0))
    report.append(("Rows in output file", len(df)))

    with pd.ExcelWriter(dst, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="cleaned", index=False)
        pd.DataFrame(report, columns=["check", "count"]).to_excel(xw, sheet_name="report", index=False)
        for name in ("cleaned", "report"):
            ws = xw.sheets[name]
            ws.freeze_panes = "A2"
            for col in ws.columns:
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(width + 2, 40)
    print("Wrote", dst)
    for k, v in report:
        print("  %-60s %s" % (k, v))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
