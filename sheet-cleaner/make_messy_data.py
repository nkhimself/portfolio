"""Creates a synthetic messy customer-orders spreadsheet (all data is invented)."""
import random
import sys
from datetime import date, timedelta

from openpyxl import Workbook

random.seed(7)

first = ["Anna", "Liam", "Sara", "Omar", "Mia", "Noah", "Eva", "Ali", "Zoe", "Ben", "Lena", "Karim"]
last = ["Smith", "Jones", "Khan", "Brown", "Miller", "Garcia", "Novak", "Rossi", "Weber", "Lopez"]
countries = ["USA", "U.S.A.", "united states", "UK", "United Kingdom", "Germany", "germany ", "Deutschland", "Canada", "CANADA"]
products = ["Notebook", "notebook ", "Pen Set", "PEN SET", "Desk Lamp", "desk lamp", "Backpack", "Mug"]


def messy_date(d):
    style = random.choice(range(5))
    if style == 0:
        return d.strftime("%Y-%m-%d")
    if style == 1:
        return d.strftime("%d/%m/%Y")
    if style == 2:
        return d.strftime("%b %d, %Y")
    if style == 3:
        return d.strftime("%d.%m.%y")
    return d.strftime("%Y/%m/%d")


def messy_phone():
    n = "".join(random.choice("0123456789") for _ in range(10))
    style = random.choice(range(4))
    if style == 0:
        return n
    if style == 1:
        return "(%s) %s-%s" % (n[:3], n[3:6], n[6:])
    if style == 2:
        return "+1 %s %s %s" % (n[:3], n[3:6], n[6:])
    return "%s.%s.%s" % (n[:3], n[3:6], n[6:])


def messy_money(x):
    style = random.choice(range(4))
    if style == 0:
        return "$%s" % format(x, ",.2f")
    if style == 1:
        return "%s USD" % x
    if style == 2:
        return str(x)
    return "%s,%02d" % (int(x), int(round((x - int(x)) * 100)))  # comma decimal


def main(out):
    wb = Workbook()
    ws = wb.active
    ws.title = "orders"
    ws.append(["  Order ID", "Customer Name", "EMAIL", "phone", "Country", "Product", "Qty", "Unit price", "Order date"])
    rows = []
    start = date(2026, 1, 5)
    for i in range(1, 61):
        name = "%s %s" % (random.choice(first), random.choice(last))
        r = random.choice(range(4))
        if r == 1:
            name = name.upper()
        elif r == 2:
            name = "  " + name.lower() + " "
        email = name.strip().lower().replace(" ", ".") + "@example.com"
        if random.random() < 0.1:
            email = ""
        elif random.random() < 0.05:
            email = email.replace("@", "")
        qty = random.choice([1, 2, 3, 5, 10, "", "two"]) if random.random() < 0.2 else random.choice([1, 2, 3, 5, 10])
        price = round(random.uniform(3, 60), 2)
        d = start + timedelta(days=random.randint(0, 200))
        rows.append(["ORD-%04d" % i, name, email, messy_phone(), random.choice(countries),
                     random.choice(products), qty, messy_money(price), messy_date(d)])
    # add exact and near duplicates, and a fully empty row
    rows.insert(10, list(rows[9]))
    rows.insert(31, list(rows[30]))
    rows.insert(45, [" ".join([""]) for _ in range(9)])
    rows.insert(50, [rows[49][0].lower()] + rows[49][1:])
    for r in rows:
        ws.append(r)
    wb.save(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "messy_orders.xlsx")
