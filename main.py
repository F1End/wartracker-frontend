"""
Primary front-end setup to run with streamlit.
"""

from pathlib import Path
import logging

import pandas as pd
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
tabs = st.tabs(["Predefined Queries", "Direct SQL Query", "Direct SQL Help", "Information", "Technical Details"])

# Tab 1: Predefined Queries
with tabs[0]:
    st.subheader("Predefined Query Filters")

    query_option = st.selectbox("Select query type", ["Day over day comparison", "General Filter"])

    options = db_tools.data_options(dbconn)
    options.load_data()

    container_general_filter = st.container()
    container_dod_comparision = st.container()

    # Query type one: General Filter
    if query_option == "General Filter":
        with container_general_filter:

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

    # Query type two: Day comparison
    elif query_option == "Day over day comparison":
        with container_dod_comparision:
            selected_date_1 = st.selectbox("Date #1", options.dates, index=len(options.dates)-1)
            selected_date_2 = st.selectbox("Date #2", options.dates, index=0)
            selected_belligerents = st.selectbox("Belligerent", ["Ukraine", "Russia"])
            group_by = st.selectbox("Group data by", ["Category", "Type", "Loss type"])

            filter_dict = {}

            if st.toggle("Detail filters", key="show_filter_tier_2"):
                selected_categories = st.multiselect("Equipment Category", options.categories,
                                                     default=options.categories[-1])
                selected_types = st.multiselect("Equipment Type", options.types, default=options.types[-1])
                selected_loss_types = st.multiselect("Loss Category", options.loss_types,
                                                     default=options.loss_types[-1])
                filter_dict["category_name"] = selected_categories
                filter_dict["type_name"] = selected_types
                filter_dict["loss_type"] = selected_loss_types

            query_1 = db_tools.dod_query(filter_dict, group_by, selected_date_1)
            query_2 = db_tools.dod_query(filter_dict, group_by, selected_date_2)

            if st.button("Show", key="run_predefined"):
                st.write("asdasd")
                logger.debug(f"Using filters: \n{filter_dict}")
                st.write(f"Using filters: \n{filter_dict}")
                with dbconn as connection:
                    logger.info(f"Running with dod query: \n{query_1}")
                    df_1 = connection.query_to_df(query_1)
                    logger.info(f"Running with dod query: \n{query_2}")
                    df_2 = connection.query_to_df(query_2)

                join_cols = df_1.columns[:-1].tolist()
                merged_df = pd.merge(df_1, df_2, on=join_cols, how="outer")
                merged_df = merged_df.fillna(0)
                merged_df["Change"] = merged_df[selected_date_1] - merged_df[selected_date_2]
                st.dataframe(merged_df)

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

# Tab 3: Direct SQL Help
with tabs[2]:
    st.subheader("SQL Help")
    st.write("Here are some query examples you can get started with.")
    st.write("Although is some information about the db structure on 'Technical Details tab', "
             "concrete examples are usually more useful.")

    st.write("")
    st.write("1. Query to connect losses with the link to their proof, "
             "while also filtering for 1st of April, for 'destroyed' vehicles in category 'tank':")
    st.code("""
            SELECT * FROM loss_item l 
            INNER JOIN proofs p 
            ON l.proof_id = p.id 
            WHERE as_of = "2025-04-01" AND loss_type = "destroyed" AND category_name = "Tanks"
            """, language="sql")

    st.write("")
    st.write("2. Query to count number of lost items "
             "as of 1st of April, for 'destroyed' vehicles in category 'tank':")
    st.code("""
            SELECT party, type_name, count(*) FROM loss_item 
            WHERE as_of = "2025-04-01" AND loss_type = "destroyed" AND category_name = "Tanks" 
            GROUP BY party, type_name 
            """, language="sql")

    st.write("")
    st.write("3. Query to count number of lost items "
             "as of 1st of April, for 'destroyed' vehicles in category 'tank' "
             "that have expression 'T-72' within their type name "
             "(so basically lost T-72s:")
    st.code("""
            SELECT party, type_name, count(*) FROM loss_item 
            WHERE as_of = "2025-04-01" AND loss_type = "destroyed" AND category_name = "Tanks" 
            AND type_name like "%T-72%" 
            GROUP BY party, type_name 
            """, language="sql")

    st.write("")
    st.write("4. Query to count number of lost items "
             "and group for each day for 'destroyed' vehicles in category 'tank' "
             "that have expression 'T-80' within their type name "
             "(so basically count of lost T-80s for each day). "
             "Plus name last column accordingly:")
    st.code("""
            SELECT as_of,  party, count(*) as "all destroyed T-80" FROM loss_item 
            WHERE loss_type = "destroyed" AND category_name = "Tanks" 
            AND type_name like "%T-80%" 
            GROUP BY as_of, party 
            """, language="sql")

# Tab 4: General information/about
with tabs[3]:
    st.subheader("About")
    st.write("The goal of this site is to present the great work Oryx had been doing"
             " on the Russo-Ukrainian war in a more searchable/comparable manner. ")
    st.write("Although updates are running on daily bases, "
             "**note that data is available only since 1st of April, 2025**.")
    st.write("Patience, data will be extended in the retroactively, "
             "but this will be gradual and will take a couple of weeks.")
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

# Tab 5: Technical data about the db and project
with tabs[4]:
    st.subheader("Structure of Data")
    st.markdown("The db contains three data tables:")
    st.markdown("1. 'summary': Daily snapshot of the high level loss count.")
    st.markdown("2. 'proofs': links to photo proofs of equipment losses."
                " All data is unique in the table. "
                "Column 'id' can be connected to 'loss_item' table's 'proof_id' column.")
    st.markdown("3. 'loss_item': Detailed daily snapshot of individual losses. "
                "Ship names below type/class level are removed on purpose. "
                "The following columns are indexed: 'as_of', 'category_name', 'type_name', 'loss_type'")

    st.subheader("Pipeline elements")
    st.markdown("Orchestration with Apache Airflow: [airflow-dags](https://github.com/F1End/airflow-dags)")

    st.markdown("Fetching and QC of web data: [webfetcher](https://github.com/F1End/webfetcher)")

    st.markdown("Parsing html into csv with beautifulsoup: [parsehtml](https://github.com/F1End/parsehtml)")

    st.markdown("Processing csv data into db tables with Pyspark: "
                "[longrow_to_db](https://github.com/F1End/longrow_to_db)")

    st.markdown("Access to data with Streamlit (this website) (hosted on Community Cloud): "
                "[wartracker-frontend](https://github.com/F1End/wartracker-frontend)")
    st.markdown("[Link to website](https://wartracker.streamlit.app/)")
    image_path = Path("WarTracker_High level.jpg")
    # st.markdown(f"![image]({image_path.as_posix()})")
    # st.markdown("![Image](https://github.com/user-attachments/assets/e72a1fd2-f36b-4e3f-ba97-7aabfb32ba33)")
    st.image(image_path)
