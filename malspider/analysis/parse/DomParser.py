#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#
import re
from scrapy.selector import Selector
from scrapy.contrib.loader import XPathItemLoader

class DomParser:
    def __init__(self,http_response):
        self.http_response = http_response
        self.sel = Selector(http_response)

    def extract_href_attr_elems(self):
        elems = self.sel.response.xpath('//*[@href]')
        for elem in elems:
            uri = elem.xpath('@href').extract()
            raw = elem.extract()

    def extract_src_attr_elems(self):
        elems = self.sel.response.xpath('//*[@src]')
        return elems

    def extract_script_elems(self):
        elems = self.sel.response.xpath('//script')
        return elems

    def extract_a_elems(self):
        elems = self.sel.response.xpath('//a')
	return elems

    def extract_style_elems(self):
        elems = self.sel.response.xpath('//style')
	return elems

    def extract_elems_with_inline_css(self):
        elems = self.sel.response.xpath('//*[@style]')
	return elems

    def extract_elems_with_css_class(self):
        elems = self.sel.response.xpath('//*[@class]')
	return elems

    def extract_elems_by_css_class(self, classname):
        elems = self.sel.response.xpath("//*[contains(@class,class_name)]") 
	return elems

    def extract_hidden_elements(self):
        hidden_elems = []
        style_elems = self.sel.response.xpath("//style")
        elems = self.sel.response.xpath("//*[not(self::img)][@src and (@width <= 1 or @height <= 1)]")
        for elem in elems:
           alert = [elem.xpath("@src").extract()[0], elem.extract(), elem]
           hidden_elems.append(alert)
        
        elems = self.sel.response.xpath("//*[not(self::img)][@src or @href]")
        for elem in elems:
            elem_width = elem.xpath("@width").extract()
            elem_height = elem.xpath("@height").extract()
            elem_src = elem.xpath("@src").extract()
            elem_href = elem.xpath("@href").extract()
 
            if elem_src and len(elem_src) > 0:
                resource = elem_src[0]
            elif elem_href and len(elem_href) > 0:
                resource = elem_href[0]
            else:
                resource = ""           

            parent = elem.xpath("parent::*")
            parent_style = elem.xpath("parent::*[@style]/@style").extract()
            if parent_style and len(parent_style) > 0:
                parent_height = re.findall(r"(?<![a-z]|\-)height\s*:\s*(-?\d+)", parent_style[0])
                parent_width = re.findall(r"(?<![a-z]|\-)width\s*:\s*(-?\d+)", parent_style[0])
                if (len(parent_height) and int(parent_height[0]) <= 1) or (len(parent_width) and int(parent_width[0]) <= 1):
                    alert = [resource, parent.extract()[0], parent]
                    hidden_elems.append(alert)

            parent_class = elem.xpath("parent::*[@class]/@class")
            if parent_class and len(parent_class) > 0:
                class_match = "(\\." + parent_class.extract()[0] + "\\s*\\w*\\s*\\{((?<={)[^}]*(?=}))\\})"
                re_css_class = re.compile(class_match,re.IGNORECASE|re.DOTALL)
                style_elem = self.sel.response.xpath("//style")
                match = style_elem.re(re_css_class)
                if len(match) > 0:
                    parent_left = re.findall(r"(?<![a-z])left\s*:\s*(-?\d+)", match[0])
                    parent_right = re.findall(r"(?<![a-z])right\s*:\s*(-?\d+)", match[0])
                    parent_top = re.findall(r"(?<![a-z])top\s*:\s*(-?\d+)", match[0])
                    parent_bottom = re.findall(r"(?<![a-z])bottom\s*:\s*(-?\d+)", match[0])   

                    if elem_width and len(elem_width) > 0 and len(parent_left) > 0:
                        offset = int(elem_width[0]) + int(parent_left[0]) 
                        if offset <= 0:
                            raw = match[0] + "\n" + parent.extract()[0]
                            alert = [resource, raw, parent]
                            hidden_elems.append(alert)
                    elif elem_height and len(elem_height) > 0 and len(parent_top) > 0:
                        offset = int(elem_height[0]) + int(parent_top[0])
                        if offset <= 0:
                            raw = match[0] + "\n" + parent.extract()[0]
                            alert = [resource,raw,parent]
                            hidden_elems.append(alert)

        return hidden_elems
