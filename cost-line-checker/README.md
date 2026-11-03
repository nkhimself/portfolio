# Cost-line checker

Checks bid or quote cost lines against historical prices and flags what needs a second look. All data here is invented.

## Files
- `bid_cost_lines.csv` - 43 cost lines (item, quantity, unit, unit price, supplier)
- `historical_prices.csv` - past prices for the same items
- `checked_report.xlsx` - output (sheets `summary`, `flagged`, `all_lines`)
- `check_costs.py` - the script
- `make_sample_data.py` - creates the invented input files

## Run it
```
pip install pandas openpyxl
python check_costs.py bid_cost_lines.csv historical_prices.csv checked_report.xlsx
python check_costs.py bid_cost_lines.csv historical_prices.csv checked_report.xlsx --tolerance 0.20
```

## What it checks
- Unit spellings are normalised (m3 / m³ / cbm, m2 / m² / sqm, ...)
- Line total = quantity x unit price
- Unit price vs the median historical price for that item (default tolerance 30%)
- Missing quantity or price
- Exact duplicate lines
- Items with no price history
- Units that differ from the item's usual unit

It never changes your numbers. It only adds a status and a note.

## Result on the sample
7 of 43 lines flagged: a price +152% above history, a price -42% below it, a missing quantity, a missing price, a duplicate line, an item with no history, and a wrong unit (tonnes for excavation).
