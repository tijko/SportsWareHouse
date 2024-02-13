#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import pymysql


@pytest.fixture(scope='session')
def mysql_db():
    # Connect to the MySQL server (change the connection parameters as needed)
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='P@55W0RD',
        db='test_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    # Create a cursor object
    cursor = connection.cursor()
    # Setup code (e.g., create tables, insert test data)
    cursor.execute("CREATE TABLE IF NOT EXISTS my_table(table_id INT PRIMARY KEY AUTO_INCREMENT, table_name VARCHAR(32) NOT NULL, table_number INT NOT NULL)")
    cursor.execute("INSERT INTO my_table(table_name, table_number) VALUES ('Test', 129384)")
    connection.commit()
    # Yield the connection to the test
    yield connection
    # Teardown code (e.g., drop tables)
    #cursor.execute("DROP TABLE IF EXISTS test_table")
    # Close the cursor and the connection
    cursor.close()
    connection.close()

def test_mysql_data(mysql_db):
    # Use the mysql_db fixture to interact with the MySQL database
    cursor = mysql_db.cursor()
    # Query the database
    cursor.execute("SELECT * FROM my_table WHERE table_id = 1")
    # Assert the result
    result = cursor.fetchone()
    assert result['table_name'] == 'Test'
    # Close the cursor (the connection will be closed automatically by the fixture)
    cursor.close()