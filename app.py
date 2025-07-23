import streamlit as st
from airtable import Airtable
import pandas as pd

# Airtable Credentials (use Streamlit secrets management for security)
KANBAN_BASE_ID = st.secrets["KANBAN_BASE_ID"]  # Secure API Base ID
EXPENSE_BASE_ID = st.secrets["EXPENSE_BASE_ID"]  # Secure Expense Base ID
API_KEY = st.secrets["AIRTABLE_API_KEY"]  # Secure API Key
KANBAN_TABLE = 'Tasks'
EXPENSE_TABLE = 'Expenses'

kanban_airtable = Airtable(KANBAN_BASE_ID, KANBAN_TABLE, API_KEY)
expense_airtable = Airtable(EXPENSE_BASE_ID, EXPENSE_TABLE, API_KEY)

st.set_page_config(page_title="John's TaskBoard & Expense Tracker", layout='wide', page_icon="🚀")

st.image('https://i.imgur.com/f1oM3aB.jpg', use_column_width=True)
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📌 John's TaskBoard & Expense Tracker</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio('Menu', ['🗂️ Kanban Board', '💰 Expense Tracker'])

if menu == '🗂️ Kanban Board':
    st.subheader('📋 Kanban Board')

    task = st.text_input('Task Name', placeholder="Enter Task Name")
    desc = st.text_area('Task Description', placeholder="Describe your task...")
    status = st.selectbox('Current Status', ['To Do', 'In Progress', 'Done'])
    date = st.date_input('Due Date')

    if st.button('➕ Add Task'):
        kanban_airtable.insert({'Task': task, 'Description': desc, 'Status': status, 'Date': str(date)})
        st.success('✅ Task Added Successfully!')

    tasks = kanban_airtable.get_all()
    df_tasks = pd.DataFrame([task['fields'] for task in tasks])

    cols = st.columns(3)
    statuses = ['To Do', 'In Progress', 'Done']

    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"## {statuses[idx]}")
            df = df_tasks[df_tasks['Status'] == statuses[idx]]
            for _, row in df.iterrows():
                st.markdown(f"---\n### {row['Task']}\n{row['Description']}\n📅 **{row['Date']}**")

else:
    st.subheader('💸 Expense Tracker')

    item = st.text_input('Expense Item', placeholder="Item name")
    amount = st.number_input('Amount ($)', min_value=0.0)
    category = st.selectbox('Category', ['Groceries', 'Bills', 'Entertainment', 'Others'])
    exp_date = st.date_input('Expense Date')

    if st.button('➕ Add Expense'):
        expense_airtable.insert({'Item': item, 'Amount': amount, 'Category': category, 'Date': str(exp_date)})
        st.success('✅ Expense Added Successfully!')

    expenses = expense_airtable.get_all()
    df_expenses = pd.DataFrame([expense['fields'] for expense in expenses])

    if not df_expenses.empty:
        st.table(df_expenses[['Item', 'Amount', 'Category', 'Date']])
        total_expense = df_expenses['Amount'].sum()
        st.markdown(f"## 💳 Total Expense: <span style='color: red;'>${total_expense:.2f}</span>", unsafe_allow_html=True)
