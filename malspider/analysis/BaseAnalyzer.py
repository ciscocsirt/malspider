#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#


from malspider.analysis.parse.DomParser import DomParser
from malspider.items import Alert
from malspider.items import PageLink
from malspider.items import WebPage

class BaseAnalyzer:
    def __init__(self, response):
        self.dom_parser = DomParser(response)
        self.response = response
        self.src_attr_elems = self.dom_parser.extract_src_attr_elems()
        self.href_attr_elems = self.dom_parser.extract_href_attr_elems()

        self.resource_elems = list()
        if self.src_attr_elems is not None:
            self.resource_elems.append(self.src_attr_elems)
        if self.href_attr_elems is not None:
            self.resource_elems.append(self.href_attr_elems)

    # return information about this particular page (ie. referring site, response status code, etc)
    def get_page_info(self):
        page = WebPage()
        page['uri'] = self.response.url
        page['status_code'] = self.response.status
        page['useragent'] = self.response.meta.get('User-Agent')
        page['referer'] = self.response.meta.get('Referer')

        if 'screenshot' in self.response.meta:
            page['screenshot'] = self.response.meta['screenshot']
            page['ssdeep_pagesource'] = str(ssdeep.hash(self.response.body))

            try:
                screenshot_hash = ssdeep.hash_from_file(self.response.meta['screenshot'])
                page['ssdeep_screenshot'] = screenshot_hash
            except:
                log.msg("Could not create hash from screenshot: " + self.response.meta['screenshot'], level=log.DEBUG)
        return page

    # return all elements on the page that contain an href or src attribute
    def get_resource_elems(self):
        elems = []
        if self.src_attr_elems is not None:
            for src_attr_elem in self.src_attr_elems:
                elem = self.gen_elem(src_attr_elem)
                elems.append(elem)

        if self.href_attr_elems is not None:
            for href_elem in self.href_attr_elems:
                elems.append(elem)

        return elems

    def gen_alert(self,reason,raw,requested_resource):
        alert = Alert()
        alert['reason'] = reason
        alert['raw'] = raw
        alert['uri'] = requested_resource
        alert['page'] = self.response.url
        return alert

    def gen_elem(self, page_elem):
         elem = PageLink() 
         elem['uri'] = page_elem.xpath('@src').extract()[0]
         elem['raw'] = page_elem.extract()
         elem['domain'] = self.response.meta['download_slot']
         return elem
