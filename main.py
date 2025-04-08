import streamlit as st
# st.set_page_config(page_title="SQLite Query App", layout="centered")

import sqlite3
import pandas as pd
from datetime import date

from src import db_tools, st_tools

st.set_page_config(page_title="War Tracker", layout="centered")

# Hard-coded database path
DB_PATH = "test_db_7.db"

# Connect to database
# @st.cache_resource
# def get_connection():
#     return sqlite3.connect(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

dbconn = db_tools.DBConn(DB_PATH)

# Streamlit page setup
st.title("SQLite Query Interface")

# Tab selection
tabs = st.tabs(["Direct SQL Query", "Predefined Queries"])

# -------- Tab 1: Direct SQL Query -------- #
with tabs[0]:
    st.subheader("Enter your SQL query below:")
    user_query = st.text_area("SQL Query", "SELECT name FROM sqlite_master WHERE type='table';")

    if st.button("Run Query", key="run_custom"):
        with dbconn as connection:
            df = connection.query_to_df(user_query)

        st.dataframe(df, hide_index=True)

# -------- Tab 2: Predefined Queries -------- #
with tabs[1]:
    st.subheader("Predefined Query Filters")

    options = db_tools.data_options(dbconn)
    options.load_data()
    print(options.dates)

    selected_date = st.multiselect("Date", options.dates, default=options.dates[-1])
    selected_belligerents = st.multiselect("Belligerent", options.belligerents, default=options.belligerents[-1])
    selected_categories = st.multiselect("Equipment Category", options.categories, default=options.categories[-1])
    selected_types = st.multiselect("Equipment Type", options.types, default=options.types[-1])
    selected_loss_types = st.multiselect("Loss Category", options.loss_types, default=options.loss_types[-1])

    base_query = """
    SELECT as_of as "Date", 
    party as "Belligerent", 
    category_name as "Equipment Category",
    type_name as "Equipment Type",
    loss_type as "Loss Category",
    count(proof_id) as "Count"
    FROM loss_item
    WHERE 1=1
    """
    group_by = """GROUP BY as_of, party, category_name, type_name, loss_type"""
    # filters =




