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
    color: ;
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
<p style='text-align:center; 
          color:#0f172a; 
          font-size:18px; 
          font-weight:bold;'>
Interactive analysis of sales, profit, customers and discounts
</p>
""", unsafe_allow_html=True)

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
# ==============================
# KPI SECTION (UPGRADED)
# ==============================
total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
total_orders = filtered_df["order_id"].nunique()
avg_order_value = total_sales / total_orders

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue ($)", f"${total_sales:,.0f}")
col2.metric("Orders", total_orders)
col3.metric("Profit ($)", f"${total_profit:,.0f}")
col4.metric("Avg Order Value ($)", f"${avg_order_value:,.2f}")

# Convert date column
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])

# Create Year column
filtered_df["Year"] = filtered_df["order_date"].dt.year

# ==============================
# YEAR TOGGLE
# ==============================

selected_year = st.radio(
    "Select Year",
    ["All", "2022", "2023", "2024"],
    horizontal=True
)

# ==============================
# FILTER DATA BY YEAR
# ==============================

if selected_year != "All":
    year_df = filtered_df[filtered_df["Year"] == int(selected_year)]
else:
    year_df = filtered_df

# ==============================
# CREATE SALES TREND DATA
# ==============================

sales_trend = (
    year_df.groupby(year_df["order_date"].dt.date)["sales"]
    .sum()
    .reset_index()
)

# ==============================
# CREATE LINE CHART
# ==============================

fig = px.line(
    sales_trend,
    x="order_date",
    y="sales",
    title="Sales Revenue Trend Over Time",
    markers=True
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Sales Revenue ($)",
    template="plotly_white"
)

# ==============================
# DISPLAY CHART
# ==============================

st.plotly_chart(fig, use_container_width=True)
# ==============================
# SALES BY YEAR
# ==============================
# Convert order_date to datetime
df["order_date"] = pd.to_datetime(df["order_date"])

# Create sales trend dataset
sales_trend = (
    filtered_df.groupby(filtered_df["order_date"].dt.date)["sales"]
    .sum()
    .reset_index()
)
fig = px.bar(
    sales_trend,
    x="order_date",
    y="sales",
    title="Sales Revenue Trend Over Time"
)

# ==============================
# TOTAL SALES BY PRODUCT CATEGORY
# ==============================

# Convert order_date to datetime
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])

# Create Year column
filtered_df["Year"] = filtered_df["order_date"].dt.year


# ==============================
# YEAR TOGGLE
# ==============================

selected_year = st.radio(
    "Select Year",
    ["All", "2022", "2023", "2024"],
    horizontal=True,
    key="year_toggle"
)


# ==============================
# FILTER DATA BASED ON YEAR
# ==============================

if selected_year != "All":
    year_df = filtered_df[filtered_df["Year"] == int(selected_year)]
else:
    year_df = filtered_df


# ==============================
# CALCULATE TOTAL SALES BY CATEGORY
# ==============================

category_sales = (
    year_df.groupby("product_category")["sales"]
    .sum()
    .reset_index()
)


# ==============================
# CREATE BAR CHART
# ==============================

fig = px.bar(
    category_sales,
    x="product_category",
    y="sales",
    color="product_category",
    title="Total Sales by Product Category",
    text_auto=True
)


# ==============================
# CHART LAYOUT
# ==============================

fig.update_layout(
    xaxis_title="Product Category",
    yaxis_title="Sales Revenue ($)",
    template="plotly_white"
)


# ==============================
# DISPLAY CHART
# ==============================

st.plotly_chart(fig, use_container_width=True)

# ==============================
# TOTAL SALES BY REGION
# ==============================

# Convert order_date to datetime
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])

# Extract year
filtered_df["Year"] = filtered_df["order_date"].dt.year


# ==============================
# YEAR TOGGLE
# ==============================

region_year = st.radio(
    "Select Year for Regional Sales",
    ["All", "2022", "2023", "2024"],
    horizontal=True,
    key="region_year_toggle"
)


# ==============================
# FILTER DATA BASED ON YEAR
# ==============================

if region_year != "All":
    region_df = filtered_df[filtered_df["Year"] == int(region_year)]
else:
    region_df = filtered_df


# ==============================
# CALCULATE SALES BY REGION
# ==============================

region_sales = (
    region_df.groupby("store_region")["sales"]
    .sum()
    .reset_index()
)


# ==============================
# CREATE PIE CHART
# ==============================

fig_region = px.pie(
    region_sales,
    names="store_region",
    values="sales",
    title="Total Sales by Region",
    hole=0.4   # makes it a doughnut chart
)


# ==============================
# DISPLAY CHART
# ==============================

st.plotly_chart(fig_region, use_container_width=True)

# ======================================
# TOP 10 PRODUCTS BY SALES
# ======================================
# Convert order_date to datetime
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])

# Extract year
filtered_df["Year"] = filtered_df["order_date"].dt.year


# ======================================
# YEAR TOGGLE
# ======================================

product_year = st.radio(
    "Select Year for Top Products",
    ["All", "2022", "2023", "2024"],
    horizontal=True,
    key="product_year_toggle"
)


# ======================================
# FILTER DATA BASED ON YEAR
# ======================================

if product_year != "All":
    product_df = filtered_df[filtered_df["Year"] == int(product_year)]
else:
    product_df = filtered_df


# ======================================
# CALCULATE TOP PRODUCTS
# ======================================

top_products = (
    product_df.groupby("product_name")["sales"]
    .sum()
    .reset_index()
    .sort_values(by="sales", ascending=False)
    .head(10)
)


# ======================================
# CREATE HORIZONTAL BAR CHART
# ======================================

fig_top_products = px.bar(
    top_products,
    x="sales",
    y="product_name",
    orientation="h",
    color="sales",
    title="Top 10 Products by Sales",
    text_auto=True
)


# ======================================
# CHART LAYOUT
# ======================================

fig_top_products.update_layout(
    xaxis_title="Sales Revenue",
    yaxis_title="Product Name",
    yaxis=dict(autorange="reversed"),  # highest on top
    template="plotly_white"
)


# ======================================
# DISPLAY CHART
# ======================================

st.plotly_chart(fig_top_products, use_container_width=True)

# =========================================
# 💼 FINANCIAL ANALYSIS SECTION
# =========================================

st.markdown("## 💼 Financial Performance Analysis")

# ===== Overall Financial Summary =====

total_sales = filtered_df["sales"].sum()
total_cost = filtered_df["cost"].sum()
total_profit = filtered_df["profit"].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenue", f"${total_sales:,.0f}")
col2.metric("💸 Total Cost", f"${total_cost:,.0f}")
col3.metric("📈 Gross Profit", f"${total_profit:,.0f}")
col4.metric("📊 Profit Margin", f"{profit_margin:.2f}%")

st.markdown("---")

# ===== Category-wise Financial Performance =====

category_finance = (
    filtered_df.groupby("product_category")[["sales", "cost", "profit"]]
    .sum()
    .reset_index()
)

category_finance["Profit Margin %"] = (
    category_finance["profit"] / category_finance["sales"] * 100
)

import plotly.express as px

fig = px.bar(
    category_finance,
    x="product_category",
    y="profit",
    color="product_category",
    text_auto=True,
    title="📊 Profit by Product Category",
    template="plotly_white"
)

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📋 Category Financial Summary Table")

st.dataframe(category_finance.style.format({
    "sales": "${:,.0f}",
    "cost": "${:,.0f}",
    "profit": "${:,.0f}",
    "Profit Margin %": "{:.2f}%"
}))

st.markdown("---")

# ===== Financial Flow (Waterfall Chart) =====

import plotly.graph_objects as go

fig2 = go.Figure(go.Waterfall(
    name="Financial Flow",
    orientation="v",
    measure=["absolute", "relative", "total"],
    x=["Revenue", "Cost", "Net Profit"],
    y=[total_sales, -total_cost, total_profit],
    text=[f"${total_sales:,.0f}",
          f"-${total_cost:,.0f}",
          f"${total_profit:,.0f}"],
    textposition="outside"
))

fig2.update_layout(
    title="💰 Revenue to Profit Flow",
    template="plotly_white",
    title_font_size=22,
    showlegend=False
)

st.plotly_chart(fig2, use_container_width=True)

fig.update_layout(
    xaxis_title="Total Sales",
    yaxis_title="Total Profit",
    title_font_size=20
)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# QUANTITY BY CATEGORY
# ==============================

qty_category = filtered_df.groupby("product_category")["quantity"].sum().reset_index()

fig6 = px.pie(
    qty_category,
    names="product_category",
    values="quantity",
    title="Quantity % Contribution by Category"
)

st.plotly_chart(fig6, use_container_width=True)

# ==============================
# CUSTOMER SALES
# ==============================

top_customers = (
    filtered_df.groupby("customer_id")["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig7 = px.bar(
    top_customers,
    x="customer_id",
    y="sales",
    title="Top 10 Customers by Sales"
)

st.plotly_chart(fig7, use_container_width=True)

# =========================================
# 💸 DISCOUNT IMPACT ANALYSIS (CLEANED)
# =========================================

st.markdown("## 💸 Discount Impact Analysis")

discount_analysis = (
    filtered_df.groupby("discount")[["sales", "profit"]]
    .sum()
    .reset_index()
)

# Convert discount to string (categorical)
discount_analysis["discount"] = discount_analysis["discount"].astype(str) + "%"

import plotly.express as px

fig = px.bar(
    discount_analysis,
    x="discount",
    y="sales",
    text_auto=True,
    title="Total Sales by Discount Level",
    template="plotly_white"
)

fig.update_layout(
    xaxis_title="Discount Level",
    yaxis_title="Total Sales",
)

st.plotly_chart(fig, use_container_width=True)

# Doughnut Chart
st.subheader("Sales Distribution by Product Category")

fig = px.pie(
    df,
    names="product_category",
    values="sales",
    hole=0.5
)

st.plotly_chart(fig)

# Calculate Profit Margin
discount_analysis["Profit Margin %"] = (
    discount_analysis["profit"] / discount_analysis["sales"] * 100
)

import plotly.graph_objects as go

fig = go.Figure()

# Sales Bar
fig.add_trace(go.Bar(
    x=discount_analysis["discount"],
    y=discount_analysis["sales"],
    name="Total Sales"
))

# Profit Line
fig.add_trace(go.Scatter(
    x=discount_analysis["discount"],
    y=discount_analysis["profit"],
    mode="lines+markers",
    name="Total Profit"
))

fig.update_layout(
    title="📊 Discount vs Sales & Profit",
    xaxis_title="Discount Level",
    yaxis_title="Amount",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 Profit Margin by Discount")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=discount_analysis["discount"],
    y=discount_analysis["Profit Margin %"],
    mode="lines+markers"
))

fig2.update_layout(
    title="Profit Margin % vs Discount",
    xaxis_title="Discount Level",
    yaxis_title="Profit Margin %",
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True)

# ==============================
# PROFIT & SALES BY CATEGORY
# ==============================

profit_sales = (
    filtered_df.groupby("product_category")[["sales", "profit"]]
    .sum()
    .reset_index()
)

fig9 = go.Figure()
fig9.add_bar(x=profit_sales["product_category"], y=profit_sales["sales"], name="Sales")
fig9.add_bar(x=profit_sales["product_category"], y=profit_sales["profit"], name="Profit")

fig9.update_layout(title="Total Sales & Profit by Category", barmode="group")

st.plotly_chart(fig9, use_container_width=True)
 

