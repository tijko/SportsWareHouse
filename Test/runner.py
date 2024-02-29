#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import pytest
import random


def mysql_connect():
    global data_hash
    global insert_data
    connection = pymysql.connect(
        unix_socket='/tmp/mysql.sock',
        user='tijko',
        password='tijko',
        db='test_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS my_table(table_id INT PRIMARY KEY AUTO_INCREMENT, table_name VARCHAR(64) NOT NULL, table_number INT NOT NULL)")
    query = "INSERT INTO my_table(table_name, table_number) VALUES (%s, %s)"
    picks = 0
    # Load data
    data_limit = 5001
    insert_data = dict()
    # Arbitary table-data from dictionary
    data_hash = {v:k for k,v in enumerate(raw_data, 1)}
    while picks < data_limit:
        # random data
        item_idx = random.randint(0, 466550)
        if insert_data.get(item_idx):
            continue
        # Check if test-db has data-item....
        member_query = f"SELECT * FROM my_table WHERE table_name = %s"
        cursor = connection.cursor()
        item = raw_data[item_idx]
        cursor.execute(member_query, (item,))
        member = cursor.fetchall()
        if member:
            # remove.....
            if len(member) == 1:
                cursor.close()
                cursor = connection.cursor()
                continue
            delete_q = f"DELETE FROM my_table WHERE table_name = %s"
            cursor.execute(delete_q, (item,))
            connection.commit()
            cursor.close()
            cursor = connection.cursor()
            continue
        item_number = data_hash[item]
        insert_data[item_number] = item
        cursor.execute(query, (item, item_number,))
        picks += 1
    connection.commit()
    #yield connection
    #cursor.execute("DROP TABLE IF EXISTS my_table")
    cursor.close()
    return connection

def run_test(connection):
    cursor = connection.cursor()
    query = "SELECT * FROM my_table WHERE table_number = %s"
    for _ in range(20):
        data_number = random.choice(list(insert_data.keys()))
        data = raw_data[data_number]
        cursor.execute(query, (data_number,))
        result = cursor.fetchone()
        if not result:
            print(data_number)
            continue
        # Assert the result
        print('Hit a match for....{}'.format(data))

def duplicate_finder(connection):
    cursor = connection.cursor()
    db_dump_q = f"SELECT * FROM my_table"
    cursor.execute(db_dump_q)
    data = cursor.fetchall()
    dump = []
    for i in data:
        if i not in dump:
            dump.append(i)
    print(dump == data)

if __name__ == '__main__':
    global raw_data
    with open('test-data.txt') as fh:
        raw_data = [s.strip('\n') for s in fh.readlines()]
    data_hash = {}
    connection = mysql_connect()
    duplicate_finder(connection)