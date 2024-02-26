#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Request(object):

    def __init__(self, raw_json):
        self.data = raw_json

    def parse_request(self, fields):
        pass

if __name__ == '__main__':
    pass