import streamlit as st
import requests
import pandas as pd
from datetime import date

# Airtable config from Streamlit secrets
AIRTABLE_API_KEY = st.secrets["airtable"]["api_key"]
KANBAN_BASE_ID = st.secrets["airtable"]["kanban_base_id"]
KANBAN_TABLE = st.secrets["airtable"]["kanban_table"]
EXPENSE_BASE_ID = st.secrets["airtable"]["expense_base_id"]
EXPENSE_TABLE = st.secrets["airtable"]["expense_table"]

HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

# Airtable API helpers
def get_records(base_id, table):
    url = f"https://api.airtable.com/v0/{base_id}/{table}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("records", [])

def create_record(base_id, table, fields):
    url = f"https://api.airtable.com/v0/{base_id}/{table}"
    data = {"fields": fields}
    response = requests.post(url, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()

def update_record(base_id, table, record_id, fields):
    url = f"https://api.airtable.com/v0/{base_id}/{table}/{record_id}"
    data = {"fields": fields}
    response = requests.patch(url, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Kanban Board", "Expense Tracker"])

# --- Kanban Board ---
if page == "Kanban Board":
    st.title("🗂️ Kanban Board")
    # Add Task Form
    with st.form("add_task"):
        name = st.text_input("Task Name")
        description = st.text_area("Description")
        due_date = st.date_input("Due Date", value=date.today())
        status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
        submitted = st.form_submit_button("Add Task")
        if submitted and name:
            create_record(KANBAN_BASE_ID, KANBAN_TABLE, {
                "Name": name,
                "Description": description,
                "Due Date": due_date.isoformat(),
                "Status": status
            })
            st.success("Task added!")
            st.experimental_rerun()

    # Fetch and display tasks
    records = get_records(KANBAN_BASE_ID, KANBAN_TABLE)
    tasks = pd.DataFrame([{
        "id": r["id"],
        "Name": r["fields"].get("Name", ""),
        "Description": r["fields"].get("Description", ""),
        "Due Date": r["fields"].get("Due Date", ""),
        "Status": r["fields"].get("Status", "")
    } for r in records])

    # Kanban columns
    cols = st.columns(3)
    statuses = ["To Do", "In Progress", "Done"]
    for i, status in enumerate(statuses):
        with cols[i]:
            st.subheader(status)
            for idx, row in tasks[tasks["Status"] == status].iterrows():
                st.markdown(f"**{row['Name']}**\n\n{row['Description']}\n\nDue: {row['Due Date']}")
                # Status update
                new_status = st.selectbox(
                    f"Move to...", statuses, index=statuses.index(status), key=f"{row['id']}_status"
                )
                if new_status != status:
                    update_record(KANBAN_BASE_ID, KANBAN_TABLE, row["id"], {"Status": new_status})
                    st.experimental_rerun()

# --- Expense Tracker ---
elif page == "Expense Tracker":
    st.title("💸 Expense Tracker")
    # Add Expense Form
    with st.form("add_expense"):
        item = st.text_input("Item Name")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        category = st.selectbox("Category", ["Groceries", "Bills", "Entertainment", "Others"])
        exp_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Add Expense")
        if submitted and item and amount > 0:
            create_record(EXPENSE_BASE_ID, EXPENSE_TABLE, {
                "Item": item,
                "Amount": amount,
                "Category": category,
                "Date": exp_date.isoformat()
            })
            st.success("Expense added!")
            st.experimental_rerun()

    # Fetch and display expenses
    records = get_records(EXPENSE_BASE_ID, EXPENSE_TABLE)
    expenses = pd.DataFrame([{
        "Item": r["fields"].get("Item", ""),
        "Amount": r["fields"].get("Amount", 0),
        "Category": r["fields"].get("Category", ""),
        "Date": r["fields"].get("Date", "")
    } for r in records])

    if not expenses.empty:
        st.dataframe(expenses)
        st.write(f"**Total Expenses:** ₹{expenses['Amount'].sum():,.2f}")
        st.bar_chart(expenses.groupby("Category")["Amount"].sum())
