# -*- coding: utf-8 -*-
#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import sys
import pkgutil
from scrapy import log
from tld import get_tld
from tld.exceptions import TldIOError,TldDomainNotFound,TldBadUrl
from urlparse import urlparse
from malspider import settings
from malspider.items import PageLink
from malspider.items import WebPage
from malspider.items import Alert
from scrapy.exceptions import DropItem


class WhitelistFilterPipeline(object):
    def process_item(self, item, spider):
        if not type(item) == Alert:
            return item

        uri = item['uri']

        if not uri:
            raise DropItem("Not a valid alert URI: ", uri)

        if spider.custom_whitelist:
            for (pattern) in spider.custom_whitelist:
                if pattern[0] in uri:
                    raise DropItem("Whitelisted domain found in Alert: ", uri)

        if spider.alexa_whitelist:
            try:
                parsed_uri = urlparse(uri)
                parsed_domain = '{uri.netloc}'.format(uri=parsed_uri)
                domain = get_tld(uri)
                for alexa_domain in spider.alexa_whitelist:
                    if domain.endswith(alexa_domain):
                        raise DropItem("Alert domain found in Alexa Whitelist: ", domain)
            except (TldIOError,TldDomainNotFound,TldBadUrl) as e:
                log.msg("Error parsing TLD. Still allowing alert for " + uri, level=log.WARNING)
            except:
                raise

        return item
