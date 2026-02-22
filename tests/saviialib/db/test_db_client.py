import unittest
from unittest.mock import MagicMock, patch

from saviialib.db import DbClient, DbClientInitArgs, ExecuteArgs, FetchAllArgs, FetchOneArgs


class TestDbClient(unittest.TestCase):
    def setUp(self):
        self.init_args = DbClientInitArgs(
            connection_string="DRIVER={SQLite3};DATABASE=test.db",
            client_name="pyodbc_client",
        )

    def test_should_raise_key_error_for_unsupported_client(self):
        args = DbClientInitArgs(
            connection_string="DRIVER={SQLite3};DATABASE=test.db",
            client_name="unsupported_client",
        )
        with self.assertRaises(KeyError):
            DbClient(args)

    @patch("saviialib.db.clients.pyodbc_client.pyodbc.connect")
    def test_should_connect_successfully(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        client = DbClient(self.init_args)
        client.connect()
        mock_connect.assert_called_once_with(self.init_args.connection_string)

    @patch("saviialib.db.clients.pyodbc_client.pyodbc.connect")
    def test_should_close_connection(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        client = DbClient(self.init_args)
        client.connect()
        client.close()
        mock_connection.cursor.return_value.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("saviialib.db.clients.pyodbc_client.pyodbc.connect")
    def test_should_execute_query(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        client = DbClient(self.init_args)
        client.connect()
        args = ExecuteArgs(query="INSERT INTO table (col) VALUES (?)", params=["value"])
        client.execute(args)
        mock_connection.cursor.return_value.execute.assert_called_once_with(
            args.query, args.params
        )

    @patch("saviialib.db.clients.pyodbc_client.pyodbc.connect")
    def test_should_fetch_all_rows(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        mock_connect.return_value = mock_connection
        client = DbClient(self.init_args)
        client.connect()
        args = FetchAllArgs(query="SELECT * FROM table")
        result = client.fetch_all(args)
        self.assertEqual(result, [("row1",), ("row2",)])

    @patch("saviialib.db.clients.pyodbc_client.pyodbc.connect")
    def test_should_fetch_one_row(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchone.return_value = ("row1",)
        mock_connect.return_value = mock_connection
        client = DbClient(self.init_args)
        client.connect()
        args = FetchOneArgs(query="SELECT * FROM table WHERE id = ?", params=[1])
        result = client.fetch_one(args)
        self.assertEqual(result, ("row1",))

    def test_should_raise_connection_error_on_execute_without_connect(self):
        client = DbClient(self.init_args)
        args = ExecuteArgs(query="SELECT 1")
        with self.assertRaises(ConnectionError):
            client.execute(args)

    def test_should_raise_connection_error_on_fetch_all_without_connect(self):
        client = DbClient(self.init_args)
        args = FetchAllArgs(query="SELECT 1")
        with self.assertRaises(ConnectionError):
            client.fetch_all(args)

    def test_should_raise_connection_error_on_fetch_one_without_connect(self):
        client = DbClient(self.init_args)
        args = FetchOneArgs(query="SELECT 1")
        with self.assertRaises(ConnectionError):
            client.fetch_one(args)
