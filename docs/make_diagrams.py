"""Draw the ShelfWise design and project-management diagrams.

Creates PNG files in docs/diagrams/. Uses Graphviz (dot) for DFDs, ERD and
architecture, and matplotlib for the use case diagram, wireframes and charts.
Usage:  python docs/make_diagrams.py
"""
import json
import os
import subprocess
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "diagrams")
os.makedirs(OUT, exist_ok=True)

BRAND, DARK, RED, AMBER, GREY, INK = "#2456a6", "#1b2a4a", "#d4543f", "#c98a12", "#8a93a0", "#1f2a3a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#b8c0cc",
                     "axes.spines.top": False, "axes.spines.right": False})


def dot(name, source):
    path = os.path.join(OUT, name + ".png")
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", path], input=source.encode(), check=True)


# ------------------------------------------------------------------ DFD level 0
dot("dfd_level0", r"""
digraph G { rankdir=LR; bgcolor=white; nodesep=0.5; ranksep=1.2; node [fontname="Helvetica", fontsize=12];
  edge [fontname="Helvetica", fontsize=10, color="#5b6575"];
  staff [shape=box, style=filled, fillcolor="#e6edf8", color="#2456a6", label="Shop Staff"];
  mgr   [shape=box, style=filled, fillcolor="#e6edf8", color="#2456a6", label="Shop Manager"];
  sys   [shape=circle, style=filled, fillcolor="#2456a6", fontcolor=white, width=2.1, label="0\nShelfWise\nKnow your\nshelves."];
  supp  [shape=box, style=filled, fillcolor="#f2f4f7", color="#8a93a0", label="Supplier"];
  cust  [shape=box, style=filled, fillcolor="#f2f4f7", color="#8a93a0", label="Customer"];
  { rank=same; staff; cust; }
  { rank=same; mgr; supp; }
  staff -> sys [label="login details, sales,\ndeliveries, waste"];
  sys -> staff [label="stock levels, sale totals,\nerror messages"];
  cust -> sys [label="product chosen,\npayment method"];
  sys -> cust [label="sale total"];
  sys -> mgr [label="low stock alerts, dashboard,\nsmart reorder, sales + profit reports"];
  mgr -> sys [label="products, prices,\nsuppliers, users, stock counts"];
  supp -> sys [label="delivery details\n(items, quantities)"];
  sys -> supp [label="reorder list (CSV)"];
}""")

# ------------------------------------------------------------------ DFD level 1
dot("dfd_level1", r"""
digraph G { rankdir=TB; bgcolor=white; nodesep=0.35; ranksep=0.65; node [fontname="Helvetica", fontsize=11];
  edge [fontname="Helvetica", fontsize=9, color="#5b6575"];
  staff [shape=box, style=filled, fillcolor="#e6edf8", color="#2456a6", label="Staff"];
  mgr   [shape=box, style=filled, fillcolor="#e6edf8", color="#2456a6", label="Manager"];
  node [shape=box, style="rounded,filled", fillcolor="#2456a6", fontcolor=white, color="#1b2a4a"];
  p1 [label="1.0\nSign in"]; p2 [label="2.0\nManage\nproducts"]; p3 [label="3.0\nReceive\nstock"];
  p4 [label="4.0\nRecord\nsale"]; p5 [label="5.0\nRecord\nwaste"]; p6 [label="6.0\nReports +\nsmart reorder"];
  node [shape=record, style=filled, fillcolor="#fff3dc", color="#c98a12", fontcolor="#1f2a3a"];
  d1 [label="D1 | Users"]; d2 [label="D2 | Products"]; d3 [label="D3 | Sales"]; d4 [label="D4 | Waste records"];
  d5 [label="D5 | Stock movements"]; d6 [label="D6 | Suppliers"]; d7 [label="D7 | Categories"];
  staff -> p1 [label="email, password"]; mgr -> p1; p1 -> d1 [dir=both, label="check hash"];
  mgr -> p2 [label="product, condition,\nprices"]; p2 -> d2; d7 -> p2 [label="category"];
  staff -> p3 [label="qty, supplier"]; d6 -> p3; p3 -> d2 [label="qty +"]; p3 -> d5 [label="IN"];
  staff -> p4 [label="product, qty,\npayment"]; d2 -> p4 [label="price, cost,\nstock"]; p4 -> d3 [label="sale"];
  p4 -> d2 [label="qty -"]; p4 -> d5 [label="SALE"];
  staff -> p5 [label="qty, reason"]; p5 -> d4; p5 -> d2 [label="qty -"]; p5 -> d5 [label="WRITE_OFF"];
  d2 -> p6; d3 -> p6; d4 -> p6; d5 -> p6; p6 -> mgr [label="reports, CSV,\nsuggested orders"];
}""")

# ------------------------------------------------------------------ ERD
def entity(name, colour, fields):
    rows = "".join(f'<tr><td align="left"{(" port=" + chr(34) + port + chr(34)) if port else ""}>{text}</td></tr>' for text, port in fields)
    return f'{name} [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4"><tr><td bgcolor="{colour}"><font color="white"><b>{name.upper()}</b></font></td></tr>{rows}</table>>];'

PK, FK = "&#128273; ", "&#9670; "
ents = "\n".join([
    entity("users", "#2456a6", [(PK + "<u>user_id</u> INT", "pk"), ("full_name VARCHAR(100)", ""), ("email VARCHAR(150) (unique)", ""), ("password_hash VARCHAR(255)", ""), ("role ENUM('manager','staff')", ""), ("is_active TINYINT(1)", ""), ("created_at DATETIME", "")]),
    entity("categories", "#2456a6", [(PK + "<u>category_id</u> INT", "pk"), ("category_name VARCHAR(80) (unique)", "")]),
    entity("suppliers", "#2456a6", [(PK + "<u>supplier_id</u> INT", "pk"), ("supplier_name VARCHAR(120) (unique)", ""), ("phone VARCHAR(30)", ""), ("email VARCHAR(150)", "")]),
    entity("products", "#1b2a4a", [(PK + "<u>product_id</u> INT", "pk"), ("sku VARCHAR(30) (unique)", ""), ("product_name VARCHAR(150)", ""), ("brand VARCHAR(60)", ""), (FK + "<i>category_id</i> INT", "cat"), ("item_condition ENUM('New','Refurbished','Used')", ""), ("cost_price DECIMAL(8,2)", ""), ("sell_price DECIMAL(8,2)", ""), ("quantity INT (CHECK &gt;= 0)", ""), ("reorder_level INT", ""), ("warranty_months INT", ""), ("is_active TINYINT(1)", ""), ("created_at DATETIME", "")]),
    entity("sales", "#2f5f9e", [(PK + "<u>sale_id</u> INT", ""), (FK + "<i>product_id</i> INT", "prod"), (FK + "<i>user_id</i> INT", "user"), ("quantity INT (&gt; 0)", ""), ("unit_price DECIMAL(8,2)", ""), ("unit_cost DECIMAL(8,2)", ""), ("total DECIMAL(10,2)", ""), ("payment_method ENUM('Cash','Card')", ""), ("sale_date DATETIME", "")]),
    entity("waste_records", "#d4543f", [(PK + "<u>waste_id</u> INT", ""), (FK + "<i>product_id</i> INT", "prod"), (FK + "<i>user_id</i> INT", "user"), ("quantity INT (&gt; 0)", ""), ("reason ENUM('Damaged','Faulty',...)", ""), ("note VARCHAR(255)", ""), ("unit_cost DECIMAL(8,2)", ""), ("waste_date DATETIME", "")]),
    entity("stock_movements", "#c98a12", [(PK + "<u>movement_id</u> INT", ""), (FK + "<i>product_id</i> INT", "prod"), (FK + "<i>user_id</i> INT", "user"), (FK + "<i>supplier_id</i> INT (optional)", "sup"), ("movement_type ENUM('IN','SALE','WRITE_OFF','ADJUST')", ""), ("quantity_change INT", ""), ("balance_after INT (&gt;= 0)", ""), ("note VARCHAR(255)", ""), ("movement_date DATETIME", "")]),
    entity("password_resets", "#6b5b95", [(PK + "<u>reset_id</u> INT", ""), (FK + "<i>user_id</i> INT", "user"), ("code_hash VARCHAR(255)", ""), ("expires_at DATETIME", ""), ("attempts INT", ""), ("used TINYINT(1)", ""), ("created_at DATETIME", "")]),
])
dot("erd", r"""
digraph G { rankdir=LR; bgcolor=white; nodesep=0.45; ranksep=1.1;
  node [shape=plain, fontname="Helvetica", fontsize=10]; edge [fontname="Helvetica", fontsize=9, color="#5b6575", arrowhead=crow, arrowtail=tee, dir=both];
""" + ents + r"""
  categories:pk:e -> products:cat:w [label="1 : many"];
  products:pk:e -> sales:prod:w [label="1 : many"];
  products:pk:e -> waste_records:prod:w [label="1 : many"];
  products:pk:e -> stock_movements:prod:w [label="1 : many"];
  users:pk:e -> sales:user:w [label="1 : many"];
  users:pk:e -> waste_records:user:w [label="1 : many"];
  users:pk:e -> stock_movements:user:w [label="1 : many"];
  users:pk:e -> password_resets:user:w [label="1 : many"];
  suppliers:pk:e -> stock_movements:sup:w [label="1 : many", arrowtail=teeodot];
}""")

# ------------------------------------------------------------------ Architecture
dot("architecture", r"""
digraph G { rankdir=TB; bgcolor=white; nodesep=0.4; ranksep=0.6; node [fontname="Helvetica", fontsize=12, shape=box, style="rounded,filled"];
  edge [fontname="Helvetica", fontsize=9, color="#5b6575"];
  subgraph cluster_c { label="Client tier"; style="rounded,dashed"; color="#8a93a0"; fontname="Helvetica";
    browser [fillcolor="#e6edf8", color="#2456a6", label="Web browser (PC, tablet or phone)\nHTML5 · CSS3 · JavaScript"]; }
  subgraph cluster_s { label="Application tier – Python Flask"; style="rounded,dashed"; color="#8a93a0"; fontname="Helvetica";
    auth  [fillcolor="#2456a6", fontcolor=white, label="auth.py\nsign-in · roles · CSRF"];
    routes [fillcolor="#2456a6", fontcolor=white, label="routes.py\nweb pages + templates"];
    stock [fillcolor="#1b2a4a", fontcolor=white, label="stock.py\nbusiness rules · reports\nsmart reorder"];
    dbpy  [fillcolor="#1b2a4a", fontcolor=white, label="db.py\nPyMySQL (SQLite for tests)"];
    auth -> routes [style=dashed, label="protects"]; routes -> stock; stock -> dbpy; }
  subgraph cluster_d { label="Data tier"; style="rounded,dashed"; color="#8a93a0"; fontname="Helvetica";
    db [shape=cylinder, fillcolor="#fff3dc", color="#c98a12", label="MySQL 8 database\n'shelfwise'\n8 tables (InnoDB)"]; }
  browser -> routes [label="HTTP request\n(GET / POST + token)"];
  routes -> browser [label="HTML page / CSV"];
  dbpy -> db [label="SQL with %s parameters\n(transactions)"];
}""")

# ------------------------------------------------------------------ Use case diagram
def stick(ax, x, y, label):
    ax.add_patch(plt.Circle((x, y + 0.55), 0.18, fill=False, lw=1.6, color=INK))
    ax.plot([x, x], [y + 0.37, y - 0.2], color=INK, lw=1.6)
    ax.plot([x - 0.3, x + 0.3], [y + 0.15, y + 0.15], color=INK, lw=1.6)
    ax.plot([x, x - 0.25], [y - 0.2, y - 0.6], color=INK, lw=1.6)
    ax.plot([x, x + 0.25], [y - 0.2, y - 0.6], color=INK, lw=1.6)
    ax.text(x, y - 0.95, label, ha="center", fontsize=11, weight="bold")


fig, ax = plt.subplots(figsize=(11, 7.6))
ax.set_xlim(0, 13); ax.set_ylim(-1.1, 10); ax.axis("off")
ax.add_patch(FancyBboxPatch((3.0, 0.3), 7.0, 9.3, boxstyle="round,pad=0.05", fc="#f6f8fc", ec=BRAND, lw=1.6))
ax.text(6.5, 9.25, "ShelfWise system", ha="center", fontsize=13, weight="bold", color=DARK)
cases = {
    "Sign in / sign out": (6.5, 8.6), "Search + filter products": (5.0, 7.6), "Receive stock": (5.0, 6.65),
    "View dashboard": (5.0, 5.7), "View stock history": (5.0, 4.75), "Record sale": (5.0, 3.8),
    "Record waste": (5.0, 2.85), "Manage products": (8.0, 7.6), "Manage suppliers": (8.0, 6.75),
    "Stock count": (8.0, 5.9), "Smart reorder report": (8.0, 5.05), "Sales + profit reports": (8.0, 4.2),
    "Export CSV": (8.0, 3.35), "Manage users": (8.0, 2.5), "Low stock alerts": (8.0, 1.65), "Check stock available": (5.0, 1.45),
}
for text, (x, y) in cases.items():
    colour = "#fde8e6" if "waste" in text.lower() else ("#e6edf8" if x < 6 or y > 8 or y < 1.5 else "#e5eefa")
    ax.add_patch(Ellipse((x, y), 2.75, 0.7, fc=colour, ec=INK, lw=1))
    ax.text(x, y, text, ha="center", va="center", fontsize=9.5)
stick(ax, 1.2, 5.2, "Staff")
stick(ax, 11.8, 5.2, "Manager")
for t in ["Sign in / sign out", "Search + filter products", "Receive stock", "Record sale", "Record waste",
          "View dashboard", "View stock history"]:
    x, y = cases[t]
    ax.plot([1.55, x - 1.35], [5.3, y], color=GREY, lw=0.9)
for t in ["Sign in / sign out", "Manage products", "Manage suppliers", "Stock count", "Smart reorder report",
          "Sales + profit reports", "Export CSV", "Manage users", "Low stock alerts"]:
    x, y = cases[t]
    ax.plot([11.45, x + 1.35], [5.3, y], color=GREY, lw=0.9)
# UML generalisation: Manager is a kind of Staff (hollow triangle points at Staff)
ax.plot([11.8, 11.8, 1.2], [3.85, -0.35, -0.35], color=INK, lw=1.2)
ax.annotate("", xy=(1.2, 4.05), xytext=(1.2, -0.35),
            arrowprops=dict(arrowstyle="-|>,head_length=0.8,head_width=0.45", fc="white", ec=INK, lw=1.2))
ax.text(6.5, -0.65, "Generalisation: a Manager can do every Staff use case", fontsize=9, ha="center", va="top", color=INK)
# «include»: Record sale and Record waste both use Check stock available
ax.annotate("", xy=(5.0, 1.82), xytext=(5.0, 2.48), arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.1, ls="--"))
ax.annotate("", xy=(3.75, 1.6), xytext=(3.62, 3.8),
            arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.1, ls="--", connectionstyle="arc3,rad=0.45"))
ax.text(5.12, 2.12, "«include» (both arrows)", fontsize=8.5, color=AMBER, ha="left")
fig.savefig(os.path.join(OUT, "use_case.png"), dpi=200, bbox_inches="tight")
plt.close(fig)


# ------------------------------------------------------------------ Wireframes
def wire(ax, title, boxes):
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 7, fc="white", ec="#555", lw=1.2))
    ax.add_patch(Rectangle((0, 6.4), 10, 0.6, fc="#e0e0e0", ec="#555", lw=1))
    ax.text(0.2, 6.7, "● ● ●   " + title, va="center", fontsize=9, color="#333")
    for (x, y, w, h, label, kind) in boxes:
        fc = {"nav": "#cfcfcf", "btn": "#9a9a9a", "input": "white", "chart": "#efefef", "kpi": "#f4f4f4",
              "table": "#fafafa", "alert": "#eaeaea"}[kind]
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="#666", lw=0.9, ls="-" if kind != "chart" else "--"))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=7.5,
                color="white" if kind == "btn" else "#333", wrap=True)


fig, axs = plt.subplots(2, 2, figsize=(12, 8.6))
wire(axs[0][0], "Sign in", [(3, 1.2, 4, 4.6, "", "kpi"), (3.4, 4.8, 3.2, 0.5, "Logo + 'Know your shelves.'", "alert"),
                             (3.4, 3.8, 3.2, 0.5, "Email", "input"), (3.4, 3.0, 3.2, 0.5, "Password", "input"),
                             (3.4, 2.1, 3.2, 0.5, "Sign in", "btn"), (3.4, 1.4, 3.2, 0.5, "Error message area", "alert")])
wire(axs[0][1], "Dashboard", [(0, 0, 1.8, 6.4, "Side menu\n\nDashboard\nNew sale\nReceive stock\nRecord waste\nProducts\nHistory\nReports*\nSuppliers*\nUsers*\n\n*manager", "nav"),
                               (2.0, 5.3, 1.9, 0.9, "Sales 7 days", "kpi"), (4.0, 5.3, 1.9, 0.9, "Profit 7 days", "kpi"),
                               (6.0, 5.3, 1.9, 0.9, "Low stock count", "kpi"), (8.0, 5.3, 1.9, 0.9, "Stock value", "kpi"),
                               (2.0, 2.6, 4.9, 2.5, "Bar chart: sales per day (14 days)", "chart"),
                               (7.0, 2.6, 2.9, 2.5, "Sales by condition\nNew / Refurbished / Used", "chart"),
                               (2.0, 0.2, 3.9, 2.2, "Low stock +\nsmart reorder table", "table"), (6.0, 0.2, 3.9, 2.2, "Best sellers table", "table")])
wire(axs[1][0], "New sale (one product)", [(0, 0, 1.8, 6.4, "Side menu", "nav"), (2.0, 5.6, 7.9, 0.6, "Message: 'Sale saved' / 'Not enough stock'", "alert"),
                                 (2.0, 4.6, 5.2, 0.6, "Product ▼  (name · condition · price · stock)", "input"),
                                 (2.0, 3.7, 2.5, 0.6, "Quantity", "input"), (4.7, 3.7, 2.5, 0.6, "Payment ▼ Card / Cash", "input"),
                                 (2.0, 2.8, 2.6, 0.5, "Total: £0.00", "kpi"), (2.0, 2.0, 5.2, 0.5, "Warning: 'Only 4 in stock'", "alert"),
                                 (2.0, 1.1, 2.0, 0.6, "Save sale", "btn"), (7.5, 0.4, 2.4, 4.8, "Recent sales\ntable", "table")])
wire(axs[1][1], "Reports (manager)", [(0, 0, 1.8, 6.4, "Side menu", "nav"),
                                       (2.0, 5.5, 1.5, 0.5, "Low + reorder", "btn"), (3.6, 5.5, 1.3, 0.5, "Slow-moving", "alert"),
                                       (5.0, 5.5, 1.3, 0.5, "Sales + profit", "alert"), (6.4, 5.5, 1.3, 0.5, "Waste", "alert"),
                                       (7.8, 5.5, 2.1, 0.5, "Download CSV", "alert"),
                                       (2.0, 4.4, 7.9, 0.8, "Filters: From | To | Group by (product / category / condition) | Update", "input"),
                                       (2.0, 0.3, 7.9, 3.8, "Report table with totals row\n(units, revenue, profit, margin, days left, suggested order)", "table")])
fig.suptitle("ShelfWise layout sketches (Design phase) – final screens built in HTML and CSS", fontsize=13, weight="bold")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "wireframes.png"), dpi=180, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------ Gantt chart (the team's plan)
W1 = date(2026, 10, 12)          # project start date in the team's Gantt chart
D = lambda text: date(2026, int(text[5:7]), int(text[8:10]))
gantt = [  # (phase, task, owner, start, end) - copied from Group_Project_Gantt_Chart.xlsx (version 2)
    (1, "Agree project scope", "Arif", "2026-10-12", "2026-10-13"),
    (1, "Research question, aim and objectives", "Arif / Sahan", "2026-10-13", "2026-10-16"),
    (1, "Assign roles & set up tools (GitHub)", "Jacob", "2026-10-14", "2026-10-15"),
    (1, "Milestone: scope & requirements signed off", "Roberto", "2026-10-16", "2026-10-16"),
    (2, "Database design: normalisation and ERD", "Jacob", "2026-10-16", "2026-10-22"),
    (2, "Database tables", "Roberto", "2026-10-16", "2026-10-22"),
    (2, "System architecture & tech stack", "Natalia", "2026-10-17", "2026-10-22"),
    (3, "Set up database", "Roberto", "2026-10-22", "2026-10-29"),
    (3, "Back end: products & inventory", "Arif", "2026-10-22", "2026-10-29"),
    (3, "Back end: sales & orders", "Arif", "2026-10-23", "2026-10-30"),
    (3, "Front end: pages & forms", "Sahan", "2026-10-23", "2026-10-31"),
    (3, "Integrate front end + back end", "Arif", "2026-10-29", "2026-11-01"),
    (4, "Testing & bug fixing", "Natalia", "2026-11-01", "2026-11-05"),
    (4, "Write report / documentation", "Natalia", "2026-10-30", "2026-11-06"),
    (4, "Prepare presentation / demo", "All", "2026-11-05", "2026-11-07"),
    (4, "Milestone: final submission", "All", "2026-11-08", "2026-11-08"),
]
PHASES = {1: ("1. Planning & Analysis", "#8fa9d6"), 2: ("2. Design", "#4e77bd"), 3: ("3. Development", BRAND), 4: ("4. Testing & Delivery", AMBER)}
rows = []
for ph in PHASES:
    items = [g for g in gantt if g[0] == ph]
    rows.append(("phase", ph, PHASES[ph][0], "", min(D(g[3]) for g in items), max(D(g[4]) for g in items)))
    rows += [("task", ph, g[1], g[2], D(g[3]), D(g[4])) for g in items]
fig, ax = plt.subplots(figsize=(12, 7.6))
for k in range(28):                       # shade weekends, as in the team's sheet
    day = W1 + timedelta(days=k)
    if day.weekday() >= 5:
        ax.axvspan(mdates.date2num(day), mdates.date2num(day) + 1, color="#f1f3f6", zorder=0)
for i, (kind, ph, name, owner, start, end) in enumerate(rows):
    y = len(rows) - i
    x0, x1 = mdates.date2num(start), mdates.date2num(end) + 1
    if kind == "phase":
        ax.barh(y, x1 - x0, left=x0, color=INK, height=0.28)
    elif name.startswith("Milestone"):
        ax.plot(x0 + 0.5, y, marker="D", ms=11, color=RED)
        ax.text(x1 + 0.2, y, owner, va="center", fontsize=8, color=GREY)
    else:
        ax.barh(y, x1 - x0, left=x0, color=PHASES[ph][1], height=0.62)
        ax.text(x1 + 0.2, y, owner, va="center", fontsize=8, color=GREY)
ax.set_yticks(range(len(rows), 0, -1))
labels = ax.set_yticklabels([("" if r[0] == "phase" else "   ") + r[2] for r in rows], fontsize=9)
for lab, r in zip(labels, rows):
    if r[0] == "phase":
        lab.set_fontweight("bold")
ax.xaxis_date()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
for w in range(5):
    ax.axvline(mdates.date2num(W1 + timedelta(days=7 * w)), color="#c8d0db", lw=0.8)
    if w < 4:
        ax.text(mdates.date2num(W1 + timedelta(days=7 * w + 3.5)), len(rows) + 0.9, f"Week {w + 1}", ha="center", fontsize=9, color=GREY)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=n) for n, c in PHASES.values()] + [plt.Line2D([], [], marker="D", ls="", color=RED, label="Milestone")],
          loc="lower left", fontsize=8, ncol=5, frameon=False)
ax.set_xlim(mdates.date2num(W1 - timedelta(days=0.5)), mdates.date2num(W1 + timedelta(days=29)))
ax.set_ylim(-0.6, len(rows) + 1.5)
ax.set_title("ShelfWise Gantt chart – Group 6 – Waterfall, 4 phases (12 Oct – 8 Nov 2026)", fontsize=12, weight="bold", pad=12)
ax.text(1.0, -0.12, "All 16 tasks: Done. Grey columns are weekends.", transform=ax.transAxes, ha="right", fontsize=8, color=GREY)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "gantt.png"), dpi=180)
plt.close(fig)

# ------------------------------------------------------------------ Milestone chart
milestones = [("M1 Scope & requirements\nsigned off", "2026-10-16", "Roberto"), ("M2 Design\ncomplete", "2026-10-22", "Jacob, Roberto,\nNatalia"),
              ("M3 Development\ncomplete", "2026-11-01", "Arif"), ("M4 Testing\ncomplete", "2026-11-05", "Natalia"),
              ("M5 Final\nsubmission", "2026-11-08", "All")]
fig, ax = plt.subplots(figsize=(12, 2.9))
ax.axhline(0, color=INK, lw=2)
for i, (label, when, who) in enumerate(milestones):
    d = (D(when) - W1).days
    ax.plot(d, 0, marker="D", ms=13, color=RED if i == 4 else BRAND)
    up = 0.35 if i % 2 == 0 else 1.35
    ax.plot([d, d], [0, up - 0.05], color="#c8d0db", lw=0.8, zorder=0)
    ax.text(d, up, label + "\n" + D(when).strftime("%a %d %b"), ha="center", va="bottom", fontsize=9, weight="bold")
    ax.text(d, -0.35 if i % 2 == 0 else -1.2, who, ha="center", va="top", fontsize=8.5, color=GREY)
ax.set_xlim(-2, 30); ax.set_ylim(-2.2, 2.6); ax.axis("off")
ax.set_title("Milestone chart – one sign-off at the end of each Waterfall phase", fontsize=12, weight="bold")
fig.savefig(os.path.join(OUT, "milestones.png"), dpi=180, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------ Waterfall model
steps = [("1. Planning &\nAnalysis", "12–16 Oct", "Scope, research question,\nrequirements, GitHub", "#8fa9d6"),
         ("2. Design", "16–22 Oct", "Normalised ERD, tables,\narchitecture", "#4e77bd"),
         ("3. Development", "22 Oct – 1 Nov", "Database, back end,\nfront end, integration", BRAND),
         ("4. Testing &\nDelivery", "30 Oct – 8 Nov", "Tests, bug fixes,\nreport, demo", AMBER)]
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.set_xlim(0, 11); ax.set_ylim(0, 5); ax.axis("off")
for i, (name, when, what, colour) in enumerate(steps):
    x, y = 0.3 + i * 2.55, 3.9 - i * 1.05
    ax.add_patch(FancyBboxPatch((x, y), 2.3, 0.85, boxstyle="round,pad=0.03", fc=colour, ec="none"))
    ax.text(x + 1.15, y + 0.5, name, ha="center", va="center", color="white", fontsize=10.5, weight="bold")
    ax.text(x + 1.15, y + 0.13, when, ha="center", va="center", color="white", fontsize=8.5)
    ax.text(x + 1.15, y - 0.12, what, ha="center", va="top", fontsize=8.5, color=INK)
    if i < 3:
        ax.annotate("", xy=(x + 2.55 + 0.2, y - 0.6), xytext=(x + 2.3, y + 0.42),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, connectionstyle="angle,angleA=0,angleB=90"))
        ax.text(x + 2.42, y + 0.55, f"◆ M{i + 1}", fontsize=8.5, color=RED, weight="bold")
ax.text(10.95, 4.55, "◆ M4 testing complete (5 Nov)\n◆ M5 final submission (8 Nov)", fontsize=9, color=RED, weight="bold", ha="right", va="top")
ax.set_title("ShelfWise Waterfall life cycle: each phase is signed off before the next starts", fontsize=12, weight="bold")
fig.savefig(os.path.join(OUT, "waterfall.png"), dpi=180, bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------ Workload per member (shared tasks count for each owner)
people = ["Arif", "Jacob", "Natalia", "Roberto", "Sahan"]
mine = lambda p, g: p in g[2] or g[2] == "All"
count = {p: sum(1 for g in gantt if mine(p, g)) for p in people}
days = {p: sum((D(g[4]) - D(g[3])).days + 1 for g in gantt if mine(p, g)) for p in people}
fig, ax = plt.subplots(figsize=(7, 3.3))
bars = ax.bar(people, [count[p] for p in people], color=BRAND)
ax.bar_label(bars, labels=[f"{count[p]} tasks\n{days[p]} days" for p in people], fontsize=8.5)
ax.set_ylim(0, max(count.values()) + 2); ax.set_ylabel("Tasks owned ('All' tasks count for everyone)")
ax.set_title("Work split from the Gantt chart", weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "workload.png"), dpi=180); plt.close(fig)

# ------------------------------------------------------------------ Evidence charts
with open(os.path.join(HERE, "evidence.json"), encoding="utf-8") as f:
    ev = json.load(f)["mysql"]
COND = {"New": "#2f5f9e", "Refurbished": "#1b6846", "Used": AMBER}   # same colours as the condition badges

fig, ax = plt.subplots(figsize=(7, 3.4))
rows = ev["sales_by_condition"]
bars = ax.barh([r["label"] for r in rows][::-1], [r["revenue"] for r in rows][::-1], color=[COND[r["label"]] for r in rows][::-1])
ax.bar_label(bars, labels=[f"£{r['revenue']:,.0f}  ({100 * r['profit'] / r['revenue']:.0f}% margin)" for r in rows][::-1], padding=4, fontsize=9)
ax.set_xlim(0, max(r["revenue"] for r in rows) * 1.5)
ax.set_xlabel("Revenue (£), 35 days of made-up data")
ax.set_title("Sales and margin by condition", weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_condition.png"), dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.8))
rows = ev["sales_by_category"]
bars = ax.barh([r["label"] for r in rows][::-1], [r["revenue"] for r in rows][::-1], color=BRAND)
ax.bar_label(bars, labels=[f"£{r['revenue']:,.0f}" for r in rows][::-1], padding=4, fontsize=9)
ax.set_xlim(0, max(r["revenue"] for r in rows) * 1.25)
ax.set_xlabel("Revenue (£), 35 days of made-up data")
ax.set_title("Revenue by category", weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_category.png"), dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.2))
rows = ev["waste_by_reason"]
bars = ax.barh([r["label"] for r in rows][::-1], [r["cost"] for r in rows][::-1], color=RED)
ax.bar_label(bars, labels=[f"£{r['cost']:,.2f}" for r in rows][::-1], padding=4, fontsize=9)
ax.set_xlim(0, max(r["cost"] for r in rows) * 1.25)
ax.set_xlabel("Cost of waste (£)")
ax.set_title("Waste by reason", weight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_waste.png"), dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.6))
groups = {"Security +\nforgot password": 9, "Products": 7, "Stock, sales\n+ waste": 14, "Reports, alerts\n+ smart reorder": 9, "Roles, users\n+ suppliers": 5, "Database\nchecks": 4, "Performance": 1}
bars = ax.bar(list(groups), list(groups.values()), color=BRAND)
ax.bar_label(bars, labels=[f"{v}/{v}" for v in groups.values()], fontsize=9)
ax.set_ylabel("Tests"); ax.set_ylim(0, 16)
ax.set_title("49 of 49 tests passed on MySQL and on SQLite", weight="bold")
plt.setp(ax.get_xticklabels(), fontsize=8.5)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_tests.png"), dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 3.4))
names = list(ev["timings"])
means = [ev["timings"][n]["mean_ms"] for n in names]
bars = ax.bar(names, means, color=BRAND)
ax.bar_label(bars, labels=[f"{m:.0f}" for m in means], fontsize=8.5)
ax.axhline(500, color=RED, ls="--"); ax.text(len(names) - 0.5, 470, "target 500 ms", color=RED, ha="right", va="top", fontsize=8)
ax.set_ylim(0, 560); ax.set_ylabel("Mean time (ms)")
ax.set_title("Page speed on MySQL (20 requests per page)", weight="bold")
plt.setp(ax.get_xticklabels(), fontsize=8.5, rotation=15)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_performance.png"), dpi=180); plt.close(fig)

print("Diagrams written to", OUT)
