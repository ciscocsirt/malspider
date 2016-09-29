# -*- coding: utf-8 -*-
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

from malspider import settings
from malspider.items import PageLink
from malspider.items import WebPage
from malspider.items import Alert
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
