"""Check bid / quote cost lines against historical prices.

Usage:
    python check_costs.py bid_cost_lines.csv historical_prices.csv report.xlsx [--tolerance 0.30]

For every line it:
  - normalises unit spellings (m3 / m³ / cbm -> m3 ...)
  - computes the line total
  - compares the unit price with the median historical price for that item
    and flags lines more than --tolerance (default 30 %) away
  - flags missing quantity or price, exact duplicate lines, items with no
    price history, and units that do not match the item's usual unit

It never changes your numbers: it only adds a 'status' and 'note' column.
Output is an Excel file with a summary sheet and the checked lines.
"""
import argparse
import sys

import pandas as pd

UNIT_MAP = {
    "m3": "m3", "m³": "m3", "cbm": "m3",
    "m2": "m2", "m²": "m2", "sqm": "m2",
    "kg": "kg", "kgs": "kg",
    "pcs": "pcs", "pc": "pcs", "pieces": "pcs",
    "m": "m", "lm": "m",
    "l": "l", "ltr": "l",
}


def norm_unit(u):
    u = str(u).strip().lower()
    return UNIT_MAP.get(u, u)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lines_csv")
    ap.add_argument("history_csv")
    ap.add_argument("out_xlsx")
    ap.add_argument("--tolerance", type=float, default=0.30)
    a = ap.parse_args()

    lines = pd.read_csv(a.lines_csv)
    hist = pd.read_csv(a.history_csv)
    hist["unit"] = hist["unit"].map(norm_unit)
    ref = hist.groupby("item").agg(ref_unit=("unit", "first"), ref_price=("unit_price_eur", "median")).reset_index()

    df = lines.copy()
    df["unit"] = df["unit"].map(norm_unit)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
    df["unit_price_eur"] = pd.to_numeric(df["unit_price_eur"], errors="coerce")
    df = df.merge(ref, on="item", how="left")
    df["line_total_eur"] = (df["qty"] * df["unit_price_eur"]).round(2)
    df["deviation_pct"] = ((df["unit_price_eur"] / df["ref_price"] - 1) * 100).round(1)

    dup_cols = ["item", "qty", "unit", "unit_price_eur", "supplier"]
    is_dup = df.duplicated(subset=dup_cols, keep="first")

    status, note = [], []
    for i, r in df.iterrows():
        issues = []
        if pd.isna(r["qty"]):
            issues.append("missing quantity")
        if pd.isna(r["unit_price_eur"]):
            issues.append("missing price")
        if is_dup[i]:
            issues.append("duplicate of an earlier line")
        if pd.isna(r["ref_price"]):
            issues.append("no price history for this item")
        else:
            if r["unit"] != r["ref_unit"]:
                issues.append("unit '%s' differs from usual '%s'" % (r["unit"], r["ref_unit"]))
            elif pd.notna(r["deviation_pct"]) and abs(r["deviation_pct"]) > a.tolerance * 100:
                issues.append("price %+.0f%% vs median history" % r["deviation_pct"])
        status.append("CHECK" if issues else "ok")
        note.append("; ".join(issues))
    df["status"], df["note"] = status, note

    out_cols = ["line", "item", "qty", "unit", "unit_price_eur", "supplier", "line_total_eur",
                "ref_price", "deviation_pct", "status", "note"]
    df = df[out_cols].rename(columns={"ref_price": "median_hist_price_eur"})

    flagged = df[df["status"] == "CHECK"]
    summary = pd.DataFrame([
        ("Lines checked", len(df)),
        ("Lines flagged for review", len(flagged)),
        ("Total of all lines (EUR, lines with qty and price)", round(df["line_total_eur"].sum(), 2)),
        ("Total of flagged lines (EUR)", round(flagged["line_total_eur"].sum(), 2)),
        ("Price tolerance used", "%d%%" % round(a.tolerance * 100)),
    ], columns=["item", "value"])

    with pd.ExcelWriter(a.out_xlsx, engine="openpyxl") as xw:
        summary.to_excel(xw, sheet_name="summary", index=False)
        flagged.to_excel(xw, sheet_name="flagged", index=False)
        df.to_excel(xw, sheet_name="all_lines", index=False)
        for name in xw.sheets:
            ws = xw.sheets[name]
            ws.freeze_panes = "A2"
            for col in ws.columns:
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(width + 2, 50)
    print(summary.to_string(index=False))
    print()
    print(flagged[["line", "item", "status", "note"]].to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
