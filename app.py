import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Load Dataset
df = pd.read_csv("retail_data.csv")

# Convert date
df["order_date"] = pd.to_datetime(df["order_date"])
df["Year"] = df["order_date"].dt.year

# ==============================
# SIDEBAR FILTERS
# ==============================

st.sidebar.header("Filters")
st.markdown("<h1 style='text-align: center;'>📊 Sales Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fa;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 2px solid #e0e0e0;
}

h1 {
    color: #1f4e79;
}

.stMetric {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
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
# KPI SECTION
# ==============================

total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
total_quantity = filtered_df["quantity"].sum()
total_orders = filtered_df["order_id"].nunique()
profit_margin = total_profit / total_sales

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Orders", total_orders)
col3.metric("Total Profit", f"${total_profit:,.2f}")
col4.metric("Total Quantity", total_quantity)
col5.metric("Profit Margin %", f"{profit_margin:.2%}")

st.markdown("---")

# ==============================
# SALES BY YEAR
# ==============================

sales_year = filtered_df.groupby("Year")["sales"].sum().reset_index()

fig1 = px.line(
    sales_year,
    x="Year",
    y="sales",
    title="Total Sales by Year",
    markers=True
)

st.plotly_chart(fig1, use_container_width=True)

# ==============================
# SALES BY CATEGORY
# ==============================

sales_category = filtered_df.groupby("product_category")["sales"].sum().reset_index()

fig2 = px.bar(
    sales_category,
    x="product_category",
    y="sales",
    title="Total Sales by Product Category",
    text_auto=True
)

st.plotly_chart(fig2, use_container_width=True)

# ==============================
# SALES BY REGION
# ==============================

sales_region = filtered_df.groupby("store_region")["sales"].sum().reset_index()

fig3 = px.bar(
    sales_region,
    x="store_region",
    y="sales",
    title="Total Sales by Store Region",
    color="store_region"
)

st.plotly_chart(fig3, use_container_width=True)

# ==============================
# TOP 10 PRODUCTS
# ==============================

top_products = (
    filtered_df.groupby("product_name")["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x="sales",
    y="product_name",
    orientation="h",
    title="Top 10 Products by Sales"
)

st.plotly_chart(fig4, use_container_width=True)

# ==============================
# PROFIT vs SALES
# ==============================

fig5 = px.scatter(
    filtered_df,
    x="sales",
    y="profit",
    color="product_category",
    title="Sales vs Profit"
)

st.plotly_chart(fig5, use_container_width=True)

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

# ==============================
# DISCOUNT ANALYSIS
# ==============================

discount_analysis = (
    filtered_df.groupby("discount")[["sales", "profit"]]
    .sum()
    .reset_index()
)

fig8 = px.bar(
    discount_analysis,
    x="discount",
    y="sales",
    title="Total Sales by Discount"
)

st.plotly_chart(fig8, use_container_width=True)

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

# ==============================
# DATA TABLE
# ==============================

st.markdown("### Detailed Data")
st.dataframe(filtered_df)
