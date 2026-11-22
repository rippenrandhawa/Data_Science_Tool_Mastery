"""LAB 4 - Python Data Visualisation.

Builds a publication-quality visualisation gallery with Matplotlib, Seaborn and
Plotly from the shared real transaction extract.

Static charts  -> outputs/charts/*.png      (200 DPI, labelled, interpreted)
Interactive    -> outputs/interactive/*.html (Plotly, hover + zoom)

Run:  python visualization_lab.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "online_retail_sales_sample.csv")
CHART_DIR = os.path.join(HERE, "outputs", "charts")
HTML_DIR = os.path.join(HERE, "outputs", "interactive")
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

PALETTE = ["#2F5597", "#4472C4", "#8FAADC", "#C55A11", "#ED7D31", "#A5A5A5",
           "#FFC000", "#548235", "#70AD47", "#7030A0"]

sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 10, "figure.dpi": 100, "savefig.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
})


def save(fig, name, caption):
    path = os.path.join(CHART_DIR, name)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {name}  - {caption}")


def load():
    df = pd.read_csv(DATA, parse_dates=["InvoiceDate"])
    df["month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
    df["value_band"] = pd.cut(df["line_total"], bins=[-np.inf, 50, 200, np.inf],
                              labels=["Small (<50)", "Medium (50-200)", "Large (200+)"])
    return df


def chart_01_monthly_revenue(df):
    monthly = df.groupby("month").agg(revenue=("line_total", "sum"),
                                      orders=("InvoiceNo", "nunique")).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(monthly["month"], monthly["revenue"], marker="o", linewidth=2.4,
            color=PALETTE[0], markersize=6)
    ax.fill_between(monthly["month"], monthly["revenue"], alpha=0.15, color=PALETTE[0])
    peak = monthly.loc[monthly["revenue"].idxmax()]
    ax.annotate(f"peak {peak['month']}\nGBP {peak['revenue']:,.0f}",
                xy=(peak["month"], peak["revenue"]), xytext=(-70, -30),
                textcoords="offset points", fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#C00000"))
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (GBP)")
    ax.set_title("Chart 1 - Monthly Revenue Trend")
    ax.tick_params(axis="x", rotation=45)
    save(fig, "01_monthly_revenue_trend.png",
         "the seeded sample peaks in January 2011")


def chart_02_revenue_by_country(df):
    country = (df.groupby("Country")["line_total"].sum()
               .sort_values(ascending=False).head(10).sort_values())
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    bars = ax.barh(country.index, country.values, color=PALETTE[1])
    ax.bar_label(bars, fmt="%.0f", fontsize=8, padding=3)
    ax.set_xlabel("Revenue (GBP)")
    ax.set_ylabel("Country")
    ax.set_title("Chart 2 - Revenue by Country (Top 10)")
    save(fig, "02_revenue_by_country.png",
         "the UK dominates; international revenue is a long tail")


def chart_03_price_distribution(df):
    prices = df.loc[df["UnitPrice"] <= 50, "UnitPrice"]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.hist(prices, bins=60, color=PALETTE[2], edgecolor="white", linewidth=0.4)
    ax.axvline(prices.median(), color="#C00000", linestyle="--", linewidth=1.6,
               label=f"median GBP {prices.median():.2f}")
    ax.axvline(prices.mean(), color="#548235", linestyle="-.", linewidth=1.6,
               label=f"mean GBP {prices.mean():.2f}")
    ax.set_xlabel("Unit price (GBP, truncated at 50 for readability)")
    ax.set_ylabel("Number of transaction lines")
    ax.set_title("Chart 3 - Unit Price Distribution")
    ax.legend(frameon=False)
    save(fig, "03_price_distribution.png",
         "right-skewed: most lines are cheap, a few are very expensive")


def chart_04_quantity_vs_price(df):
    sample = df.sample(n=min(4000, len(df)), random_state=42)
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    sc = ax.scatter(sample["UnitPrice"], sample["Quantity"], s=14, alpha=0.45,
                    c=sample["line_total"], cmap="viridis", edgecolors="none")
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Unit price (GBP)")
    ax.set_ylabel("Quantity on the line")
    ax.set_title("Chart 4 - Quantity vs Unit Price")
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Line total (GBP)")
    save(fig, "04_quantity_vs_unit_price.png",
         "no strong linear link between price and quantity bought")


def chart_05_invoice_value_box(df):
    invoice = df.groupby("InvoiceNo")["line_total"].sum().reset_index()
    top5 = (df.groupby("Country")["line_total"].sum().sort_values(ascending=False)
            .head(5).index.tolist())
    data = [invoice.loc[df["Country"] == c, "line_total"].clip(upper=1500).values
            for c in top5]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.boxplot(data, tick_labels=top5, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor=PALETTE[3], alpha=0.7),
               medianprops=dict(color="white", linewidth=2))
    ax.set_xlabel("Country")
    ax.set_ylabel("Invoice value (GBP, capped at 1,500)")
    ax.set_title("Chart 5 - Invoice Value Distribution by Country (Top 5)")
    save(fig, "05_invoice_value_by_country.png",
         "overseas wholesale accounts place much larger orders than UK retail")


def chart_06_correlation_heatmap(df):
    cols = ["Quantity", "UnitPrice", "line_total"]
    corr = df[cols].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="RdBu_r", center=0,
                square=True, linewidths=0.8, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title("Chart 6 - Spearman Correlation Heatmap")
    save(fig, "06_correlation_heatmap.png",
         "line total is driven by quantity and price together")


def chart_07_value_band(df):
    band = df.groupby("value_band", observed=True).agg(
        lines=("line_total", "size"), revenue=("line_total", "sum")).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    axes[0].bar(band["value_band"].astype(str), band["lines"], color=PALETTE[4])
    axes[0].set_title("Number of lines by value band")
    axes[0].set_ylabel("Lines")
    axes[1].pie(band["revenue"], labels=band["value_band"].astype(str), autopct="%1.1f%%",
                colors=[PALETTE[4], PALETTE[5], PALETTE[6]], startangle=90)
    axes[1].set_title("Revenue share by value band")
    save(fig, "07_value_band_profile.png",
         "a small number of large lines carries most of the revenue")


def chart_08_top_products(df):
    top = (df.groupby("Description")["line_total"].sum()
           .sort_values(ascending=False).head(10).sort_values())
    fig, ax = plt.subplots(figsize=(10, 5.6))
    bars = ax.barh(top.index.str.slice(0, 38), top.values, color=PALETTE[7])
    ax.bar_label(bars, fmt="%.0f", fontsize=8, padding=3)
    ax.set_xlabel("Revenue (GBP)")
    ax.set_ylabel("Product")
    ax.set_title("Chart 8 - Top 10 Products by Revenue")
    save(fig, "08_top_products_revenue.png",
         "revenue is concentrated in a handful of gift lines")


def build_interactive(df):
    monthly = df.groupby("month").agg(revenue=("line_total", "sum"),
                                     orders=("InvoiceNo", "nunique")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"],
                             mode="lines+markers", name="Revenue (GBP)",
                             line=dict(color="#2F5597", width=3),
                             fill="tozeroy"))
    fig.add_trace(go.Bar(x=monthly["month"], y=monthly["orders"], name="Orders",
                         marker_color="#ED7D31", opacity=0.55, yaxis="y2"))
    fig.update_layout(
        title="Interactive - Monthly Revenue and Order Count",
        xaxis_title="Month", yaxis_title="Revenue (GBP)",
        yaxis2=dict(title="Orders", overlaying="y", side="right"),
        hovermode="x unified", template="plotly_white",
        xaxis=dict(rangeslider=dict(visible=True)), height=560)
    path = os.path.join(HTML_DIR, "interactive_monthly_dashboard.html")
    fig.write_html(path, include_plotlyjs="cdn")
    print(f"  saved interactive_monthly_dashboard.html")

    country = (df.groupby("Country").agg(revenue=("line_total", "sum"),
                                         orders=("InvoiceNo", "nunique"))
               .reset_index().sort_values("revenue", ascending=False).head(12))
    fig2 = px.scatter(country, x="orders", y="revenue", size="revenue",
                      color="revenue", hover_name="Country",
                      color_continuous_scale="Viridis",
                      title="Interactive - Countries: Orders vs Revenue",
                      labels={"orders": "Distinct orders", "revenue": "Revenue (GBP)"})
    fig2.update_layout(template="plotly_white", height=560)
    fig2.write_html(os.path.join(HTML_DIR, "interactive_country_scatter.html"),
                    include_plotlyjs="cdn")
    print("  saved interactive_country_scatter.html")


def main():
    print("LAB 4 - PYTHON DATA VISUALISATION")
    df = load()
    print(f"dataset: {len(df):,} lines, GBP {df['line_total'].sum():,.2f}")
    chart_01_monthly_revenue(df)
    chart_02_revenue_by_country(df)
    chart_03_price_distribution(df)
    chart_04_quantity_vs_price(df)
    chart_05_invoice_value_box(df)
    chart_06_correlation_heatmap(df)
    chart_07_value_band(df)
    chart_08_top_products(df)
    build_interactive(df)
    print(f"\nLAB 4 COMPLETE - {len(os.listdir(CHART_DIR))} PNGs, "
          f"{len(os.listdir(HTML_DIR))} interactive HTML files")


if __name__ == "__main__":
    main()
