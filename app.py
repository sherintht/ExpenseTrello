import firebase_admin
from firebase_admin import credentials, firestore
import json
import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file (for local development)
load_dotenv()

# Determine if running in Streamlit Cloud or locally
is_streamlit_cloud = "STREAMLIT_RUNTIME" in os.environ

# Check if we're using Streamlit secrets (Cloud) or .env (local development)
if is_streamlit_cloud:
    # Streamlit Cloud - Use Streamlit secrets to load Firebase service account credentials
    firebase_secret = st.secrets["firebase_service_account"]

    # Parse the secret (it's a string, so we need to load it into a dictionary)
    try:
        firebase_credentials = json.loads(firebase_secret)  # Convert JSON string into dictionary
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except ValueError as e:
        st.error(f"Error initializing Firebase: {e}")
        raise e
else:
    # Local Development - Use .env file to load the service account key path
    service_account_key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    if not service_account_key_path:
        st.error("Firebase service account key path is not set in the environment variable.")
    else:
        try:
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        except ValueError as e:
            st.error(f"Error initializing Firebase: {e}")
            raise e

# Function to register user (Sign Up)
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user
    except Exception as e:
        return None

# Function to sign in user (Login)
def sign_in_user(email):
    try:
        user = auth.get_user_by_email(email)
        return user
    except auth.UserNotFoundError:
        return None

# Function to add a task
def add_task(user_id, task_name):
    task_data = {
        'user_id': user_id,
        'task': task_name,
        'status': 'To-Do',
        'created_at': firestore.SERVER_TIMESTAMP
    }
    task_ref = db.collection('tasks').add(task_data)
    return task_ref

# Function to display tasks for a user
def display_tasks(user_id):
    tasks_ref = db.collection('tasks').where('user_id', '==', user_id).stream()
    tasks = [task.to_dict() for task in tasks_ref]
    for task in tasks:
        st.write(f"Task: {task['task']} - Status: {task['status']}")

# Function to add an expense
def add_expense(user_id, date, category, vendor, amount, payment_type, notes):
    expense_data = {
        'user_id': user_id,
        'date': date,
        'category': category,
        'vendor': vendor,
        'amount': amount,
        'payment_type': payment_type,
        'notes': notes
    }
    expense_ref = db.collection('expenses').add(expense_data)
    return expense_ref

# Function to display expenses for a user
def display_expenses(user_id):
    expenses_ref = db.collection('expenses').where('user_id', '==', user_id).stream()
    expenses = [expense.to_dict() for expense in expenses_ref]
    for expense in expenses:
        st.write(f"Date: {expense['date']} | Category: {expense['category']} | Amount: ${expense['amount']}")

# Streamlit UI
st.title("Task and Expense Manager")

# Register/Login Section
email = st.text_input("Email")
password = st.text_input("Password", type='password')

if st.button("Login"):
    user = sign_in_user(email)
    if user:
        st.sidebar.title(f"Welcome, {email}")
        st.sidebar.write(f"User ID: {user.uid}")

        # Add Task
        task_name = st.text_input("New Task")
        if st.button("Add Task"):
            add_task(user.uid, task_name)
            st.success("Task added successfully!")

        # Display User's Tasks
        st.header("Your Tasks")
        display_tasks(user.uid)

        # Add Expense
        st.header("Add Expense")
        expense_date = st.date_input("Expense Date", value=datetime.today())
        category = st.selectbox("Category", ["Food", "Transportation", "Entertainment", "Other"])
        vendor = st.text_input("Vendor")
        amount = st.number_input("Amount", min_value=0.0)
        payment_type = st.selectbox("Payment Type", ["Cash", "Credit", "Debit"])
        notes = st.text_area("Notes")

        if st.button("Add Expense"):
            add_expense(user.uid, expense_date, category, vendor, amount, payment_type, notes)
            st.success("Expense added successfully!")

        # Display User's Expenses
        st.header("Your Expenses")
        display_expenses(user.uid)

# Sign Up Section
if st.button("Sign Up"):
    user = register_user(email, password)
    if user:
        st.success(f"User {email} registered successfully! You can now log in.")
    else:
        st.error("There was an error with registration. Please try again.")
