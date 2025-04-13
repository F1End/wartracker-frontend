"""
Classes/functions for database interaction
"""
from typing import Union
from pathlib import Path
import sqlite3
import logging

import pandas as pd
import streamlit as st


logger = logging.getLogger(__name__)


@st.cache_resource
class DBConn:
    def __init__(self, db_path: Union[Path, str]):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.cursor = self.conn.cursor()
        logger.debug(f"Opened connection to {self.db_path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
        logger.debug(f"Closed connection to {self.db_path}")

    def run_query(self, sql: str) -> [list, list[tuple]]:
        logger.debug(f"Running query: {sql}")
        results = self.cursor.execute(sql).fetchall()
        columns = [description[0] for description in self.cursor.description] if self.cursor.description else []
        return columns, results

    def query_to_df(self, sql: str) -> pd.DataFrame:
        columns, results = self.run_query(sql)
        df = pd.DataFrame(results, columns=columns)
        return df


class data_options:
    def __init__(self, _db: DBConn):
        self.db = _db
        self.dates = None
        self.belligerents = None
        self.categories = None
        self.types = None
        self.loss_types = None
        self.col_map = {self.dates: "as_of",
                        self.belligerents: "party",
                        self.categories: "category_name",
                        self.types: "type_name",
                        self.loss_types: "loss_type"}

    def load_data(self):
        self.dates = self._get_distinct_values("as_of")
        self.belligerents = self._get_distinct_values("party") + ["ALL"]
        self.categories = self._get_distinct_values("category_name") + ["ALL"]
        self.types = self._get_distinct_values("type_name") + ["ALL"]
        self.loss_types = self._get_distinct_values("loss_type") + ["ALL"]

    def _get_distinct_values(self, col_name: str) -> list:
        sql = f"SELECT DISTINCT {col_name} FROM loss_item"
        with self.db as connection:
            _, results = connection.run_query(sql)
        val_list = [item[0] for item in results]
        return val_list


def generate_filter(col_name: str, selection: list) -> str:
    if selection == [] or "ALL" in selection:
        return ""
    else:
        values = [f"'{val}'" for val in selection]
        return f" AND {col_name} in ({','.join(values)})"


def sql_filters(filters: dict):
    sql_filter = ""
    for col, values in filters.items():
        sql_filter += generate_filter(col, values)
    return sql_filter


def preset_query(filter_dict: dict):
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
    group_by = """ GROUP BY as_of, party, category_name, type_name, loss_type"""
    filters = sql_filters(filter_dict)
    query = base_query + filters + group_by
    return query
