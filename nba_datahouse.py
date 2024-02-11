#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mysql.connector


class DataHouse(object):

    def __init__(self, unix_socket, db, user, passwd):
        # XXX initialize with query....
        # CREATE DATABASE nba_stats;
        # USE nba_stats;
        # CREATE TABLE IF NOT EXISTS teams(team_id INT PRIMARY KEY AUTO_INCREMENT,
        #                                  team_name VARCHAR(50),
        #                                  team_conference VARCHAR(32),
        #                                  team_division VARCHAR(32));
        # CREATE TABLE IF NOT EXISTS games(game_id INT PRIMARY KEY AUTO_INCREMENT,
        #                                  home_team_id INT, FOREIGN KEY (home_team_id)
        #                                  REFERENCES teams(team_id),
        #                                  away_team_id INT, FOREIGN KEY (away_team_id)
        #                                  REFERENCES teams(team_id),
        #                                  home_score INT NOT NULL, away_score INT NOT NULL,
        #                                  game_date DATE NOT NULL);
        self.unix_socket = unix_socket
        self.user = user
        self.db = db
        self.passwd = passwd
        self.insert_team = f"INSERT INTO teams (team_name, team_conference, team_division) VALUES (%s, %s, %s)"
        self.insert_game = f"INSERT INTO games (home_score, away_score, game_date) VALUES (%s, %s, %s)"

    @property
    def connect(self):
        try:
            self.conn = mysql.connector.connect(unix_socket=self.unix_socket,
                                                user=self.user,
                                                password=self.passwd,
                                                database=self.db)
        except mysql.connector.Error as error:
            print(f"Error: {error}")
            sys.exit()

    @property
    def clear_teams(self):
        cur = self.conn.cursor()
        query = f"DELETE FROM teams"
        cur.execute(query)
        # XXX 'commit' is pivotal....
        self.conn.commit()
        cur.close()

    def team_exists(self, team_name):
        cursor = self.conn.cursor()
        query = f"SELECT * FROM teams WHERE team_name = %s"
        cursor.execute(query, (team_name,))
        team = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        return team != []        

    def insert(self, query, data):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            self.conn.commit()
            print('Data loaded successfully')
        except:
            print('Insert ERROR!')
            sys.exit()
        finally:
            if self.conn.is_connected():
                cursor.close()
                #self.conn.close()
                #print('MySQL connection is closed')
