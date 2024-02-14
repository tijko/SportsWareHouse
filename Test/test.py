#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import pytest
import random


@pytest.fixture(autouse=True)
def mysql_db():
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='P@55W0RD',
        db='test_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS my_table(table_id INT PRIMARY KEY AUTO_INCREMENT, table_name VARCHAR(32) NOT NULL, table_number INT NOT NULL)")
    query = "INSERT INTO my_table(table_name, table_number) VALUES (%s, %s)"
    picks = 0
    # Load data
    global data_hash
    global raw_data
    global insert_data
    with open('test-data.txt') as fh:
        raw_data = [s.strip('\n') for s in fh.readlines()]
    data_limit = 5000
    insert_data = dict()
    # Arbitary table-data from dictionary
    data_hash = {v:k for k,v in enumerate(raw_data, 1)}
    while picks < data_limit:
        # random data
        item_idx = random.randint(0, 466550)
        if insert_data.get(item_idx):
            continue
        item = raw_data[item_idx]
        item_number = data_hash[item]
        insert_data[item_number] = item
        cursor.execute(query, (item, item_number,))
        print('Insert: {} to {}'.format(item, item_number))
        picks += 1
    connection.commit()
    yield connection
    # Close the cursor and the connection
    cursor.close()
    connection.close()

def test_mysql_data(mysql_db):
    # Use the mysql_db fixture to interact with the MySQL database
    cursor = mysql_db.cursor()
    query = "SELECT * FROM my_table WHERE table_number = %s"
    for _ in range(20):
        data_number = random.choice(list(insert_data.keys()))
        data = insert_data[data_number]
        cursor.execute(query, (data_number,))
        result = cursor.fetchone()
        if not result:
            continue
        print('Found.....{}'.format(data_number))
        # Assert the result
        assert result['table_name'] == data
        print('Hit a match for....{}'.format(data))
    # Close the cursor (the connection will be closed automatically by the fixture)
    cursor.close()