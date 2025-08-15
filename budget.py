import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set Streamlit page configuration
st.set_page_config(page_title="Financial Budget Tracker", layout="wide")

st.title("💸 Financial Budget Tracker Dashboard")

# Sidebar for uploading data and inputting budget
st.sidebar.header("Upload Your Financial Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

st.sidebar.header("Set Your Monthly Budgets")
categories = ['Housing', 'Food', 'Transport', 'Entertainment', 'Healthcare', 'Utilities', 'Other']
budgets = {}
for cat in categories:
    budgets[cat] = st.sidebar.number_input(f"{cat} Budget", min_value=0, value=1000, step=50)

# Sample data structure
def sample_data():
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    data = {
        'Date': np.random.choice(dates, 100),
        'Category': np.random.choice(categories, 100),
        'Amount': np.random.randint(10, 500, 100),
        'Type': np.random.choice(['Expense', 'Income'], 100, p=[0.8, 0.2])
    }
    return pd.DataFrame(data)

# Load data
if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=['Date'])
else:
    st.info("No file uploaded. Using sample data.")
    df = sample_data()

# Data preprocessing
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.strftime('%Y-%m')

# Dashboard KPIs
total_income = df[df['Type'] == 'Income']['Amount'].sum()
total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
net_savings = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${total_expense:,.2f}")
col3.metric("Net Savings", f"${net_savings:,.2f}", delta=f"${net_savings:,.2f}")

st.markdown("----")
st.header("🧾 Expenses by Category")

# Group by category
category_expense = df[df['Type'] == 'Expense'].groupby('Category')['Amount'].sum().reindex(categories, fill_value=0)

# Compare with budgets
budget_df = pd.DataFrame({
    'Budget': pd.Series(budgets),
    'Spent': category_expense
})
budget_df['Remaining'] = budget_df['Budget'] - budget_df['Spent']
budget_df['Status'] = np.where(budget_df['Remaining'] >= 0, 'Within Budget', 'Over Budget')

st.dataframe(budget_df.style.applymap(
    lambda x: 'color: green;' if isinstance(x, str) and x == 'Within Budget' else 'color: red;' if isinstance(x, str) else ''
), height=300)

# Seaborn bar chart for category expenses
fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.barplot(x=budget_df.index, y=budget_df['Spent'], ax=ax1, palette='viridis')
ax1.axhline(y=budget_df['Budget'].mean(), color='red', linestyle='--', label='Avg Budget')
ax1.set_ylabel('Amount Spent')
ax1.set_title('Expenses by Category')
ax1.legend()
st.pyplot(fig1)

st.markdown("----")
st.header("📈 Monthly Trends")

# Monthly expense vs income line chart
monthly = df.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
fig2, ax2 = plt.subplots(figsize=(10, 4))
monthly.plot(kind='line', marker='o', ax=ax2)
ax2.set_ylabel('Amount')
ax2.set_title('Monthly Income & Expenses')
st.pyplot(fig2)

# Expense breakdown pie chart
st.header("🍕 Expense Breakdown")
fig3, ax3 = plt.subplots()
category_expense.plot.pie(autopct='%1.1f%%', ax=ax3, startangle=90, colors=sns.color_palette('pastel'))
ax3.set_ylabel('')
ax3.set_title('Expense Distribution')
st.pyplot(fig3)

# Data Explorer
st.markdown("----")
st.header("🔎 Data Explorer")
st.dataframe(df.sort_values('Date', ascending=False).reset_index(drop=True))

st.success("Tip: Upload your own CSV with columns: Date, Category, Amount, Type (Income/Expense) for personalized analytics!")