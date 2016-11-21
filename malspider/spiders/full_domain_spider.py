# -*- coding: utf-8 -*-
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import yara
import scrapy
import MySQLdb
import pkgutil
from scrapy import log
from scrapy import Selector
from scrapy.http import Request
from malspider.scrapy_webdriver.http import WebdriverRequest
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
from malspider import settings
from bson.objectid import ObjectId

#from malspider.parser.LinkParser import LinkParser
#from malspider.parser.DomParser import DomParser
#from malspider.analyzer.URLClassifier import URLClassifier
#from malspider.analyzer.DomInspector import DomInspector
from malspider.analysis.Analyzer import Analyzer
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from urlparse import urlparse
from malspider.items import WebPage
from malspider.items import Alert

class FullDomainSpider(CrawlSpider):
    name = settings.BOT_NAME
    already_crawled = set()
    pages_crawled = 0

    def __init__(self, *args, **kwargs):
        super(FullDomainSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = kwargs.get('allowed_domains').split(',')
        self.org = kwargs.get('org')
        self.start_urls = kwargs.get('start_urls').split(',')
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self, spider):
        self.conn = MySQLdb.connect(host=settings.MYSQL_HOST, db=settings.MYSQL_DB, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD, charset='utf8', use_unicode=True)
        cursor = spider.conn.cursor()
        sql_str = "SELECT pattern from whitelist"
        cursor.execute(sql_str)
        self.custom_whitelist = cursor.fetchall()
        try:
            alexa_whitelist_file = pkgutil.get_data("malspider", "resources/alexa-1k-whitelist.csv").decode('ascii')
            self.alexa_whitelist = alexa_whitelist_file.splitlines()
        except:
            log.msg("Error loading alexa whitelist...", level=log.ERROR)

    def spider_closed(self, spider):
        try:
            self.conn.close()
        except:
            los.msg("Could not close database connection", level=log.ERROR)

    def process_value(self,value):
        return value

    def start_requests(self):
        for url in self.start_urls:
            yield WebdriverRequest(url, callback=self.parse_response)
 
    def parse_response(self, response):
        page_id = ObjectId()

        analyzer = Analyzer(response)
        alerts = analyzer.inspect_response()
        elems = analyzer.get_resource_elems()
        page = analyzer.get_page_info()

        for alert in alerts:
            alert['org_id'] = self.org
            yield alert

        for elem in elems:
            elem['page_id'] = page_id
            elem['org_id'] = self.org
            yield elem

        page['page_id'] = page_id
        page['org_id'] = self.org
        yield page

        #limit page depth
        if self.pages_crawled >= settings.PAGES_PER_DOMAIN:
            return

        for link in LxmlLinkExtractor(unique=True, deny_extensions=list(), allow_domains=self.allowed_domains).extract_links(response):
            if not link.url in self.already_crawled and self.pages_crawled <= settings.PAGES_PER_DOMAIN:
                self.already_crawled.add(link.url)
                self.pages_crawled = self.pages_crawled + 1
                log.msg("Yielding request for " + link.url, level=log.INFO)
                yield WebdriverRequest(link.url, callback=self.parse_response)
            elif self.pages_crawled >= settings.PAGES_PER_DOMAIN:
                log.msg("Reached max crawl depth: " + str(settings.PAGES_PER_DOMAIN), level=log.INFO)
                return
            else:
                log.msg("avoiding duplicate request for: " + link.url, level=log.INFO)
