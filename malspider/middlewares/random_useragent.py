#!/usr/bin/python
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import pkgutil
import os
import random
from scrapy import signals
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware

class RandomUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, settings):
        super(RandomUserAgentMiddleware, self).__init__()
        
        try:
            ua_file = pkgutil.get_data("malspider", "resources/useragents.txt").decode('ascii')
            self.ualist = ua_file.splitlines()
        except:
            self.ualist = [settings.get('USER_AGENT')]
       
    @classmethod
    def from_crawler(cls, crawler):
        my_obj = cls(crawler.settings)
        crawler.signals.connect(my_obj.spider_opened,signal=signals.spider_opened)
        return my_obj

    def process_request(self, request, spider):
        rand_ua = random.choice(self.ualist)
        if rand_ua:
            request.headers.setdefault('User-Agent', rand_ua)
