# -*- coding: utf-8 -*-
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import scrapy
from scrapy import log
from scrapy import Selector
from scrapy.http import Request
from malspider.scrapy_webdriver.http import WebdriverRequest
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider,Rule
from malspider import settings
from bson.objectid import ObjectId

from malspider.parser.LinkParser import LinkParser
from urlparse import urlparse

from malspider.items import WebPage

class FullDomainSpider(CrawlSpider):
    name = settings.BOT_NAME
    already_crawled = set()

    def __init__(self, *args, **kwargs):
        super(FullDomainSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = kwargs.get('allowed_domains').split(',')
        self.org = kwargs.get('org')
        self.start_urls = kwargs.get('start_urls').split(',')

    def process_value(self,value):
        return value

    def start_requests(self):
        for url in self.start_urls:
            yield WebdriverRequest(url, callback=self.parse_item)
 
    def parse_item(self, response):
        sel = Selector(response)
        items = LinkParser.extract_page_links(sel)
        num_onsite_links = 0
        num_offsite_links = 0

        page_id = ObjectId()

        for item in items:
            item['page_id'] = page_id
            item['domain'] = ""
            item['org_id'] = self.org
            item['referer'] = response.meta.get('Referer')

            if 'uri' in item:
                parse_uri = urlparse(item['uri'])
                item['domain'] = parse_uri[1]

            item['onsite'] = False
            for dom in self.allowed_domains:
                if item['domain'] == "" or item['domain'] in dom:
                    item['onsite'] = True
                    num_onsite_links = num_onsite_links + 1

            if item['onsite'] == False:
                num_offsite_links = num_offsite_links + 1

            yield item

        page = LinkParser.get_page_data(response)
        page['page_id'] = page_id
        page['useragent'] = response.meta.get('User-Agent')
        page['referer'] = response.meta.get('Referer')
        page['org_id'] = self.org
        page['num_offsite_links'] = num_offsite_links
        page['num_onsite_links'] = num_onsite_links

        yield page

        for link in LxmlLinkExtractor(unique=True).extract_links(response):
            if not link.url in self.already_crawled:
                self.already_crawled.add(link.url)
                yield WebdriverRequest(link.url, callback=self.parse_item)
            else:
                print "avoiding request for: ", link.url

