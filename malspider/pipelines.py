# -*- coding: utf-8 -*-
#
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.  
#

import sys
import ssdeep
import time
import MySQLdb
from datetime import datetime
from scrapy import signals
from bson.objectid import ObjectId

from malspider import settings
from malspider.items import PageLink
from malspider.items import WebPage

from scrapy.exceptions import DropItem

class DuplicateFilterPipeline(object):
    def __init__(self):
        self.extracted_links = set()

    def process_item(self, item, spider):
        if not type(item) == PageLink:
            return item

        if 'raw' in item:
            if item['raw'] in self.extracted_links:
                raise DropItem("Duplicate item found: ", item['raw'])
            else:
                self.extracted_links.add(item['raw'])
        return item

class MySQLPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host=settings.MYSQL_HOST, db=settings.MYSQL_DB, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD, charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            item_type = type(item)
            if item_type == WebPage:
                spider.log("Adding page item to database...")
                sql_str = self.build_sql_string(item, "page")
                result = self.cursor.execute(sql_str, item.values())
                self.conn.commit()
                spider.log("Successfully added page to database.")
            elif item_type == PageLink:
                spider.log("Attempting to add element to database...")
                sql_str = self.build_sql_string(item, "element")
                results = self.cursor.execute(sql_str, item.values())
                self.conn.commit()
                spider.log("Successfully added element to database.")
        except Exception, e:
            spider.log(str(e))

        return item


    def build_sql_string(self, item, table_name):
        sql_cols = []
        sql_vals = []
        for key in item:
            sql_cols.append(key)
            sql_vals.append("%s")

        sql_cols_str = ",".join(map(str, sql_cols))
        sql_vals_str = ",".join(map(str, sql_vals))
        sql_str = """INSERT INTO  %s (%s)""" % (table_name, sql_cols_str)
        sql_str = sql_str + """ VALUES (""" + sql_vals_str + """)"""

        return sql_str
