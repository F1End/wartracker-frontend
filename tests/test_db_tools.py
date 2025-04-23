import unittest

from src import db_tools


class TestSQLFilters(unittest.TestCase):

    def test_generate_filter_all(self):
        self.assertEqual(db_tools.generate_filter("category", ["ALL"]), "")

    def test_generate_filter_empty_selection(self):
        self.assertEqual(db_tools.generate_filter("category", []), "")

    def test_generate_filter_single_value(self):
        self.assertEqual(db_tools.generate_filter("category", ["Tanks"]), " AND category in ('Tanks')")

    def test_generate_filter_multiple_values(self):
        self.assertEqual(
            db_tools.generate_filter("category", ["Tanks", "IFVs"]),
            " AND category in ('Tanks','IFVs')"
        )

    def test_sql_filters_empty_dict(self):
        self.assertEqual(db_tools.sql_filters({}), "")

    def test_sql_filters_all_values(self):
        self.assertEqual(db_tools.sql_filters({"category_name": ["ALL"], "loss_type": ["ALL"]}), "")

    def test_sql_filters_mixed_values(self):
        filters = {
            "category": ["Tanks", "IFVs"],
            "loss_type": ["damaged"],
            "loss_id": ["ALL"]
        }
        expected = " AND category in ('Tanks','IFVs') AND loss_type in ('damaged')"
        self.assertEqual(db_tools.sql_filters(filters), expected)

    def test_sql_filters_single_filter(self):
        filters = {"category": ["Tanks", "IFVs"]}
        expected = " AND category in ('Tanks','IFVs')"
        self.assertEqual(db_tools.sql_filters(filters), expected)


if __name__ == '__main__':
    unittest.main()
