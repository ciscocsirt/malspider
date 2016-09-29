# -*- coding: utf-8 -*-
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import MySQLdb
from malspider.items import PageLink
from malspider.items import WebPage
from malspider.items import Alert
from scrapy.exceptions import DropItem


class MySQLPipeline(object):
    def process_item(self, item, spider):
        cursor = spider.conn.cursor()
        try:
            item_type = type(item)
            if item_type == WebPage:
                spider.log("Adding page item to database...")
                sql_str = self.build_sql_string(item, "page")
                result = cursor.execute(sql_str, item.values())
                spider.conn.commit()
                spider.log("Successfully added page to database.")
            elif item_type == PageLink:
                spider.log("Attempting to add element to database...")
                sql_str = self.build_sql_string(item, "element")
                results = cursor.execute(sql_str, item.values())
                spider.conn.commit()
                spider.log("Successfully added element to database.")
            elif item_type == Alert:
                spider.log("Attempting to add element to database...")
                sql_str = self.build_sql_string(item, "alert")
                results = cursor.execute(sql_str, item.values())
                spider.conn.commit()
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
