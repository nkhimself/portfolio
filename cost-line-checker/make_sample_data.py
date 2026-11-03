"""Creates synthetic bid cost lines + a historical price list (all numbers invented)."""
import csv
import random

random.seed(11)

# item, canonical unit, typical unit price (EUR)
ITEMS = [
    ("Concrete C25/30", "m3", 118.0),
    ("Rebar 12mm", "kg", 1.05),
    ("Plywood 18mm", "m2", 22.5),
    ("Insulation board 100mm", "m2", 14.8),
    ("Cement bags 25kg", "pcs", 6.4),
    ("Excavation", "m3", 11.5),
    ("Roof tiles", "m2", 31.0),
    ("Copper pipe 22mm", "m", 9.9),
    ("Drywall 12.5mm", "m2", 5.6),
    ("Interior paint", "l", 7.2),
]
UNIT_VARIANTS = {
    "m3": ["m3", "m³", "cbm", "M3"],
    "m2": ["m2", "m²", "sqm", "M2"],
    "kg": ["kg", "KG", "kgs"],
    "pcs": ["pcs", "pc", "pieces", "PCS"],
    "m": ["m", "lm", "M"],
    "l": ["l", "L", "ltr"],
}
SUPPLIERS = ["Nordbygg AB", "Baumarkt GmbH", "Stenhus Oy", "Bouw & Co"]


def main():
    with open("historical_prices.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "unit", "date", "unit_price_eur"])
        for item, unit, p in ITEMS:
            for m in range(1, 9):
                w.writerow([item, unit, "2026-%02d-15" % m, round(p * random.uniform(0.92, 1.08), 2)])

    rows = []
    for i in range(1, 41):
        item, unit, p = random.choice(ITEMS)
        qty = random.choice([4, 12, 35, 80, 150, 600, 2000])
        price = p * random.uniform(0.9, 1.1)
        rows.append([i, item, qty, random.choice(UNIT_VARIANTS[unit]), "%.2f" % price, random.choice(SUPPLIERS)])
    # planted problems for the checker to find
    base = {name: price for name, _, price in ITEMS}
    rows[3][4] = "%.2f" % (base[rows[3][1]] * 2.6)  # price far too high
    rows[8][4] = "%.2f" % (base[rows[8][1]] * 0.6)  # price far too low
    rows[14][2] = ""                                # missing quantity
    rows[20][4] = ""                                # missing price
    rows.append(list(rows[5]))                      # exact duplicate line
    rows.append([99, "Scaffolding rental", 1, "week", "850.00", "Nordbygg AB"])  # not in history
    rows.append([100, "Excavation", 40, "tonnes", "11.50", "Stenhus Oy"])        # wrong unit for item

    with open("bid_cost_lines.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["line", "item", "qty", "unit", "unit_price_eur", "supplier"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
