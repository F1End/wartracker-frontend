"""
Primary front-end setup to run with streamlit.
"""

from pathlib import Path
import logging

import streamlit as st

from src import db_tools


logger = logging.getLogger(__name__)
level = logging.INFO
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=level)

st.set_page_config(page_title="War Tracker", layout="centered", )
st.title("War Tracker v0.1")

DB_PATH = Path("data", "wartracker.db")
dbconn = db_tools.DBConn(DB_PATH)


# Tabs
tabs = st.tabs(["Predefined Queries", "Direct SQL Query", "Information", "Technical details"])

# Tab 1: Predefined Queries
with tabs[0]:
    st.subheader("Predefined Query Filters")

    options = db_tools.data_options(dbconn)
    options.load_data()

    selected_date = st.multiselect("Date", options.dates, default=options.dates[-1])
    selected_belligerents = st.multiselect("Belligerent", options.belligerents, default=options.belligerents[-1])
    selected_categories = st.multiselect("Equipment Category", options.categories, default=options.categories[-1])
    selected_types = st.multiselect("Equipment Type", options.types, default=options.types[-1])
    selected_loss_types = st.multiselect("Loss Category", options.loss_types, default=options.loss_types[-1])
    filter_dict = {"as_of": selected_date, "party": selected_belligerents,
                   "category_name": selected_categories, "type_name": selected_types,
                   "loss_type": selected_loss_types}
    query = db_tools.preset_query(filter_dict)

    if st.button("Show", key="run_predefined"):
        logger.debug(f"Using filters: \n{filter_dict}")
        logger.info(f"Running with predefined query: \n{query}")
        with dbconn as connection:
            df = connection.query_to_df(query)

        st.dataframe(df, hide_index=True)

# Tab 2: Direct SQL Query
with tabs[1]:
    st.subheader("Enter your SQL query below:")
    user_query = st.text_area("SQL Query",
                              "SELECT name FROM sqlite_master WHERE type='table';"
                              "\n--you can comment out parts of the query with double-dash")

    if st.button("Run Query", key="run_custom"):
        logger.info(f"Received user query: {user_query}")
        with dbconn as connection:
            df = connection.query_to_df(user_query)

        st.dataframe(df, hide_index=True)

# Tab 3: General information/about
with tabs[2]:
    st.subheader("About")
    st.write("The goal of this site is to present the great work Oryx had been doing"
             " on the Russo-Ukrainian war in a more searchable/comparable manner. ")
    st.write("The site contains snapshots of losses from the Oryx's website. "
             "Each date in the database refers to the day when the loss was parsed from their pages. "
             "After each parsing all data is re-uploaded to the database. "
             "Hence, if noone from Oryx made any changes between two parsing, two days data may entirely be identical."
             )

    st.write("")
    st.subheader("Sources:")
    st.write("https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html")
    st.write("https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html")

    st.subheader("Other:")
    st.write("I have tried to faithfully store all data,"
             " but parsing such volume of unstructured and constantly updated information is its own art."
             " Should you notice any discrepancies, please reach out to me at @reddit "
             "or via the github profile presented on the Technical Details tab.")

# Tab 4: Technical data about the db and project
with tabs[3]:
    st.subheader("Structure of Data")
    st.markdown("The db contains three data tables:")
    st.markdown("1. 'summary': Daily snapshot of the high level loss count.")
    st.markdown("2. 'proofs': links to photo proofs of equipment losses."
                " All data is unique in the table. "
                "Column 'id' can be connected to 'loss_item' table's 'proof_id' column.")
    st.markdown("3. 'loss_item': Detailed daily snapshot of individual losses."
                " Ship names below type/class level are removed on purpose.")

    st.subheader("Pipeline elements")
    st.markdown("TBD")
