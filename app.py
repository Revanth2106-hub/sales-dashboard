import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==============================
# DARK BLUE THEME STYLE
# ==============================

st.markdown("""
<style>

.stApp {
    background-color: #f0f2f6;
    color: #0f172a;
}

section[data-testid="stSidebar"] {
    background-color: #123a63;
}

</style>
""", unsafe_allow_html=True)

# Load Dataset
df = pd.read_csv("retail_data.csv")


st.markdown(
"""
<h1 style='text-align:center;color:#1f4e79'>
📊 Retail Sales Performance Dashboard
</h1>
<p style='text-align:center; color:#475569; font-size:16px;'>
Use the filters in the sidebar to focus on regions, categories, and dates. Each section below has a short explanation so you can read the charts easily.
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# Convert date
df["order_date"] = pd.to_datetime(df["order_date"])
df["Year"] = df["order_date"].dt.year

# ==============================
# SIDEBAR FILTERS
# ==============================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(120deg,#f6f9fc,#eef2f7);
}

h1, h2, h3 {
    color:#1f4e79;
}

section[data-testid="stSidebar"] {
    background-color:#ffffff;
    border-right:2px solid #e6e6e6;
}

.stMetric {
    background:white;
    padding:20px;
    border-radius:15px;
    border-left:5px solid #4CAF50;
    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
}

.block-container {
    padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)    

region = st.sidebar.multiselect(
    "Select Store Region",
    df["store_region"].unique(),
    default=df["store_region"].unique()
)

category = st.sidebar.multiselect(
    "Select Product Category",
    df["product_category"].unique(),
    default=df["product_category"].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["order_date"].min(), df["order_date"].max()]
)

filtered_df = df[
    (df["store_region"].isin(region)) &
    (df["product_category"].isin(category)) &
    (df["order_date"] >= pd.to_datetime(date_range[0])) &
    (df["order_date"] <= pd.to_datetime(date_range[1]))
]
# Convert date columns once
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])
filtered_df["Year"] = filtered_df["order_date"].dt.year
filtered_df["YearMonth"] = filtered_df["order_date"].dt.to_period("M")

year_months = sorted(filtered_df["YearMonth"].unique())
month_labels = [p.to_timestamp().strftime("%b %Y") for p in year_months]
month_options = ["All Months"] + month_labels

def _filter_by_month(df, selected):
    if selected == "All Months":
        return df
    sel_ix = month_labels.index(selected)
    return df[df["YearMonth"] == year_months[sel_ix]]

# ==============================
# KEY NUMBERS
# ==============================
st.markdown("### 📈 Key Numbers")
st.caption("Totals for the selected month or full period.")
month_kpi = st.selectbox("Month", options=month_options, index=0, key="month_kpi")
df_kpi = _filter_by_month(filtered_df, month_kpi)

total_sales = df_kpi["sales"].sum()
total_profit = df_kpi["profit"].sum()
total_orders = df_kpi["order_id"].nunique()
avg_order_value = total_sales / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_sales:,.0f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Total Profit", f"${total_profit:,.0f}")
col4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

st.markdown("---")

# ==============================
# 1. SALES REVENUE OVER TIME
# ==============================
st.markdown("### 📈 Sales Revenue Over Time")
st.caption("Daily sales trend for the selected month or full period.")
month_trend = st.selectbox("Month", options=month_options, index=0, key="month_trend")
df_trend = _filter_by_month(filtered_df, month_trend)

sales_trend = (
    df_trend.groupby(df_trend["order_date"].dt.date)["sales"]
    .sum()
    .reset_index()
)
fig_trend = px.line(sales_trend, x="order_date", y="sales", markers=True)
fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Sales Revenue ($)",
    yaxis=dict(tickformat=",", tickprefix="$"),
    template="plotly_white",
    title=""
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ==============================
# 2. BY CATEGORY & BY REGION (side by side) — Bar + Sunburst
# ==============================
st.markdown("### 🏷️ Sales Performance by Category & Region")
st.caption("Understand which product categories drive revenue and how sales are distributed across store regions.")

month_cat_region = st.selectbox(
    "Select Month",
    options=month_options,
    index=0,
    key="month_cat_region"
)

df_cat_region = _filter_by_month(filtered_df, month_cat_region)

# ===============================
# Data Preparation
# ===============================
category_sales = (
    df_cat_region.groupby("product_category")["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
)

region_sales = (
    df_cat_region.groupby("store_region")["sales"]
    .sum()
    .reset_index()
)

# ===============================
# LEFT: Category Revenue Chart
# ===============================
fig_cat = px.bar(
    category_sales,
    x="product_category",
    y="sales",
    color="product_category",
    text="sales",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_cat.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False
)

fig_cat.update_layout(
    template="plotly_white",
    xaxis_title="Product Category",
    yaxis_title="Revenue ($)",
    yaxis=dict(tickformat="$,"),
    showlegend=False,
    margin=dict(t=30, b=20, l=20, r=20)
)

# ===============================
# RIGHT: Regional Sales Share
# ===============================
fig_region = px.pie(
    region_sales,
    names="store_region",
    values="sales",
    hole=0.55,
    color_discrete_sequence=px.colors.sequential.Blues_r
)

fig_region.update_traces(
    textinfo="percent",
    textfont_size=14,
    pull=[0.03]*len(region_sales)
)

fig_region.update_layout(
    template="plotly_white",
    margin=dict(t=30, b=20, l=20, r=20)
)

# ===============================
# Layout
# ===============================
col_cat, col_region = st.columns(2)

with col_cat:
    st.plotly_chart(fig_cat, use_container_width=True)

with col_region:
    st.plotly_chart(fig_region, use_container_width=True)

st.markdown("---")
# ======================================
# 3. TOP 10 PRODUCTS & TOP 10 CUSTOMERS (side by side)
# ======================================
st.markdown("### 🏆 Top Revenue Drivers")
st.caption("Top performing products and customer contribution to total revenue.")

month_top = st.selectbox("Month", options=month_options, index=0, key="month_top")
df_top = _filter_by_month(filtered_df, month_top)

# =========================
# Data Preparation
# =========================
top_products = (
    df_top.groupby("product_name")["sales"]
    .sum()
    .reset_index()
    .sort_values(by="sales", ascending=False)
    .head(10)
)

top_customers = (
    df_top.groupby("customer_id")["sales"]
    .sum()
    .reset_index()
    .sort_values(by="sales", ascending=False)
    .head(10)
)

# =========================
# LEFT: Top Products Chart
# =========================
fig_top_products = px.bar(
    top_products,
    x="sales",
    y="product_name",
    orientation="h",
    color="sales",
    color_continuous_scale="Blues",
    text="sales"
)

fig_top_products.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False
)

fig_top_products.update_layout(
    template="plotly_white",
    xaxis_title="Revenue ($)",
    yaxis_title="Product",
    yaxis=dict(autorange="reversed"),
    xaxis=dict(tickformat="$,"),
    margin=dict(t=30, b=20, l=20, r=20),
    coloraxis_showscale=False
)

# =========================
# RIGHT: Customer Revenue Share
# =========================
fig_top_cust = px.pie(
    top_customers,
    values="sales",
    hole=0.6,
    color_discrete_sequence=px.colors.sequential.Greens_r
)

fig_top_cust.update_traces(
    textinfo="percent",
    pull=[0.03]*len(top_customers)
)

fig_top_cust.update_layout(
    template="plotly_white",
    showlegend=False,
    margin=dict(t=20, b=20, l=20, r=20)
)

# =========================
# Layout
# =========================
col_prod, col_cust = st.columns(2)

with col_prod:
    st.plotly_chart(fig_top_products, use_container_width=True)

with col_cust:
    st.plotly_chart(fig_top_cust, use_container_width=True)

st.markdown("---")
# =========================================
# 4. REVENUE & UNITS BY CATEGORY — Treemap + Sunburst
# =========================================
st.markdown("## 💼 Revenue & Units by Category")
st.caption("Left: treemap — revenue per category (size = sales). Right: sunburst — units sold per category.")
month_rev_units = st.selectbox("Month", options=month_options, index=0, key="month_rev_units")
df_rev_units = _filter_by_month(filtered_df, month_rev_units)

category_finance = (
    df_rev_units.groupby("product_category")[["sales", "cost", "profit"]]
    .sum()
    .reset_index()
)
qty_category = df_rev_units.groupby("product_category")["quantity"].sum().reset_index()

# Left: treemap (unique)
fig_fin_cat = px.treemap(
    category_finance,
    path=["product_category"],
    values="sales",
    color="sales",
    color_continuous_scale="Blues"
)
fig_fin_cat.update_traces(textinfo="label+value", texttemplate="%{label}<br>$%{value:,.0f}")
fig_fin_cat.update_layout(template="plotly_white", title="", margin=dict(t=20, b=20, l=20, r=20))

# Right: sunburst (unique)
fig_qty = px.sunburst(
    qty_category,
    path=["product_category"],
    values="quantity",
    color="quantity",
    color_continuous_scale="Greens"
)
fig_qty.update_traces(textinfo="label+value+percent parent", texttemplate="%{label}<br>%{value:,.0f} units<br>%{percentParent}")
fig_qty.update_layout(template="plotly_white", title="", margin=dict(t=20, b=20, l=20, r=20))

col_fin, col_qty = st.columns(2)
with col_fin:
    st.plotly_chart(fig_fin_cat, use_container_width=True)
with col_qty:
    st.plotly_chart(fig_qty, use_container_width=True)

st.markdown("---")

# =========================================
# 5. DISCOUNT IMPACT & SALES SHARE — Funnel + Treemap
# =========================================
st.markdown("## 💸 Discount Impact & Sales Share")
st.caption("Left: funnel — revenue at each discount level (narrowing by level). Right: treemap — sales share by category.")
month_discount = st.selectbox("Month", options=month_options, index=0, key="month_discount")
df_discount = _filter_by_month(filtered_df, month_discount)

discount_analysis = (
    df_discount.groupby("discount")[["sales", "profit"]]
    .sum()
    .reset_index()
)
discount_analysis["discount_label"] = discount_analysis["discount"].astype(str) + "%"
discount_analysis = discount_analysis.sort_values("discount")  # 0% first (widest in funnel)

# Left: funnel (unique)
fig_disc = px.funnel(
    discount_analysis,
    x="sales",
    y="discount_label",
    color="discount_label"
)
fig_disc.update_traces(
    textinfo="value",
    texttemplate="$%{x:,.0f}"
)

fig_disc.update_layout(
    xaxis_title="Total Sales ($)",
    yaxis_title="Discount Level",
    template="plotly_white",
    title="",
    showlegend=False
)
# Right: treemap (sales share by category)
cat_sales_share = df_discount.groupby("product_category")["sales"].sum().reset_index()
fig_sales_share = px.treemap(
    cat_sales_share,
    path=["product_category"],
    values="sales",
    color="sales",
    color_continuous_scale="Oranges"
)
fig_sales_share.update_traces(textinfo="label+value+percent parent", texttemplate="%{label}<br>$%{value:,.0f}<br>%{percentParent}")
fig_sales_share.update_layout(template="plotly_white", title="", margin=dict(t=20, b=20, l=20, r=20))

col_disc, col_share = st.columns(2)
with col_disc:
    st.plotly_chart(fig_disc, use_container_width=True)
with col_share:
    st.plotly_chart(fig_sales_share, use_container_width=True)

