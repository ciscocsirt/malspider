# -*- coding: utf-8 -*-
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#
from scrapy.item import Item, Field

class PageLink(Item):
    page_id = Field()
    uri = Field()
    domain = Field()
    org_id = Field()
    tag_name = Field()
    tag_details = Field()
    referer = Field()
    onsite = Field()
    raw = Field()
    attr_width = Field()
    attr_height = Field()
    attr_type = Field()
    attr_text = Field()
    attr_script_type = Field()
    attr_language = Field()
    css_attr_top = Field()
    css_attr_bottom = Field()
    css_attr_left = Field()
    css_attr_right = Field()
    css_attr_visibility = Field()
    css_class = Field()

class WebPage(Item):
    id = Field()
    page_id = Field()
    uri = Field()
    org_id = Field()
    referer = Field()
    useragent = Field()
    status_code = Field()
    content_type = Field()
    screenshot = Field()
    ssdeep_screenshot = Field()
    ssdeep_pagesource = Field()
    num_onsite_links = Field()
    num_offsite_links = Field()

class Alert(Item):
    reason = Field()
    raw = Field()
    uri = Field()
    page = Field()
    page_id = Field()
    org_id = Field()
