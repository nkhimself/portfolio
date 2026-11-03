# Orders spreadsheet cleaner

Turns a messy orders spreadsheet into a clean one and writes a report of every change. All data here is invented.

## Files
- `messy_orders.xlsx` - input (64 rows: mixed date and price formats, odd phone numbers, duplicates, a blank row)
- `cleaned_orders.xlsx` - output (sheet `cleaned` and sheet `report`)
- `clean_sheet.py` - the script
- `make_messy_data.py` - creates the invented input file

## Run it
```
pip install pandas openpyxl
python clean_sheet.py messy_orders.xlsx cleaned_orders.xlsx
```

## What it does
- Normalises column names and trims text
- Fixes name capitalisation, country names and product names
- Parses dates in five formats into YYYY-MM-DD (slash dates are read day/month/year)
- Converts "$12.50", "12.50 USD" and "12,50" into numbers
- Standardises phone numbers to +1 XXX XXX XXXX
- Flags missing or invalid emails and quantities instead of guessing
- Removes empty rows and duplicate orders (same order ID, ignoring case)
- Adds a line total and a `report` sheet with counts for each check

## Result on the sample
64 rows in, 60 rows out: 1 empty row and 3 duplicates removed, 14 emails and 2 quantities flagged.

## Assumptions to confirm on a real job
Slash dates as day/month/year, phone numbers as 10-digit US numbers, prices in USD.
