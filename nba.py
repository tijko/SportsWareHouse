#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from nba_datahouse import *
from bs4 import BeautifulSoup

import sys
import subprocess

from parse_request import *


class FrontPage(object):

    def __init__(self, api_endpoint, db_conn):
        self.api_endpoint = api_endpoint
        self.page = None
        self.data = None
        self.db_conn = db_conn

    @property
    def populate(self):
        req = requests.get(self.api_endpoint)
        if not req.ok:
            raise(requests.RequestException)
        self.page = req.text
        self.data = json.loads(self.page) # Meta & Data fields .... 
                                          # (again this is a convention and 
                                          #  can be off)
                                          # 
                                          # 'current_page':1 'next_page':2 
                                          # 'per_page':25
    def parse_page(self):
        games = self.data['data']
        #print('Clearing Table "teams"....')
        #self.db_conn.clear_teams
        print('Cycling Games....')
        for game in games:
            # Meta
            date = game['date']
            game_id = game['id']
            season = game['season']
            print('Date: {}'.format(date))
            print('Game-ID: {}'.format(game_id))
            print('Season: {}'.format(season))
            # Home
            home_team = game['home_team']
            home_name = home_team['full_name']
            home_score = game['home_team_score']
            home_conf = home_team['conference']
            home_div = home_team['division']
            print('Home: {}\nDivision: {}\nConference: {}'.format(home_name, 
                                                                  home_div, 
                                                                  home_conf))
            away_team = game['visitor_team']
            away_name = away_team['full_name']
            away_div = away_team['division']
            away_conf = away_team['conference']
            away_score = game['visitor_team_score']
            print('Away: {}\nDivision: {}\nConference: {}'.format(away_name, 
                                                                  away_div, 
                                                                  away_conf))
            winner = away_name if away_score > home_score else home_name
            winner_score = away_score if away_score > home_score else home_score
            loser = home_name if home_score < away_score else away_name
            loser_score = home_score if home_score < away_score else away_score
            print('Final: {} {} {} {}'.format(winner, 
                                              winner_score, 
                                              loser, 
                                              loser_score))
            if not self.db_conn.team_exists(home_name):
                print('Inserting {}'.format(home_name))
                self.db_conn.insert(self.db_conn.insert_team, (home_name, 
                                                               home_conf, 
                                                               home_div))
            if not self.db_conn.team_exists(away_name):
                print('Inserting {}'.format(away_name))
                self.db_conn.insert(self.db_conn.insert_team, (away_name, 
                                                               away_conf, 
                                                               away_div))
            print('')

def command_stub(query_cmd, cmd_args):
    fmt_cmd = query_cmd.format(*cmd_args)
    process = subprocess.Popen(['curl {} --silent'.format(fmt_cmd)], 
                                 stdout=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def request_stub(query_cmd, *query_args, **headers):
    fmt_cmd = query_cmd.format(*query_args)
    req = requests.get(fmt_cmd, headers=headers['headers'])
    return req.ok

def init_database(user, passwd, db, socket, endpoint):
    print('Attempting to connect Database "nba-stats"')
    nba_datahouse = DataHouse(socket, db, user, passwd)
    nba_datahouse.connect
    print('Connected to Database "nba-stats"')
    nba_front_page = FrontPage(endpoint, nba_datahouse)
    print('Hitting endpoint -> {}'.format(endpoint))
    nba_front_page.populate
    print('Parsing JSON results....')
    nba_front_page.parse_page()
    print('Finished!')


if __name__ == '__main__':
    api_endpoint = 'https://www.balldontlie.io/api/v1/games'
    api_key = '927849b5-7388-4d13-bdce-0a16575ceb5a'
    stat_query_cmd = "https://api.balldontlie.io/v1/{} -H 'Authorization:{}'"
    stat_query_req = "https://api.balldontlie.io/v1/{}"
    print(request_stub(stat_query_req, 'stats?seasons[]=2023', 
                           headers={'Authorization':api_key}))
    unix_socket = '/tmp/mysql.sock'
    database = 'nba_stats'
    user = 'tijko'
    #init_database(user, user, database, unix_socket, api_endpoint)