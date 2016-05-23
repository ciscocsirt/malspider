#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#

import sys
import md5
import ssdeep
import re

from scrapy.selector import Selector
from scrapy import log

from malspider.items import PageLink
from malspider.items import WebPage

class LinkParser:
    re_css_position = re.compile('position\\s*:\\s*(absolute)\\s*;',re.IGNORECASE|re.DOTALL)
    #re_css_class = re.compile('(\\.(?:[a-z][a-z]*[0-9]+[a-z0-9]*))\\s*\\w*\\s*\\{((?<={)[^}]*(?=}))\\}',re.IGNORECASE|re.DOTALL)
    re_css_class = re.compile('(\\.(?:[a-z0-9]*))\\s*\\w*\\s*\\{((?<={)[^}]*(?=}))\\}',re.IGNORECASE|re.DOTALL)
    re_css_position_attributes = re.compile('(top|left|right|bottom)\\s*:\\s*([-+]\\d+)\\s*px\\s*',re.IGNORECASE|re.DOTALL)
    re_css_hidden_visibility = re.compile('visibility\\s*:\\s*hidden\\s*;',re.IGNORECASE|re.DOTALL)

    @staticmethod
    def extract_page_links(sel):
        items = []

        style_nodes = sel.xpath("//style")
        for node in style_nodes:
            #extract style nodes
            raw = node.extract()
            #item = PageLink()
            #item['tag_name'] = 'style'
            #item['raw'] = node.extract()
            #items.append(item)


            #TODO:  CLEANUP this code!
            #look for css classes that contain a position and negative positionings
            #ie.  position: absolute; top: -1000px; left: -1000px;
            #this can be used to hide an iframe
            css_classes = LinkParser.re_css_class.findall(raw)

            if css_classes is not None:
                for css_class in css_classes:
                    #css_class[0] contains class name
                    #css_class[1] contains the styling information contained between {}
                    if len(css_class) >= 1:
                        css_position = LinkParser.re_css_position.search(css_class[1])
                        css_position_attributes = LinkParser.re_css_position_attributes.findall(css_class[1])
                        css_hidden_visibility = LinkParser.re_css_hidden_visibility.findall(css_class[1])
                        found = False
                        hidden = False
                        pos_attributes = {}
                        style_item = PageLink()
                        if len(css_hidden_visibility) > 0:
                            hidden = True
                            style_item['css_attr_visibility'] = 'hidden'

                        style_item['tag_name'] = 'style'
                        style_item['css_class'] = css_class[0]
                        style_item['raw'] = raw

                        if css_position is not None and css_position_attributes is not None:
                            for pos_attr in css_position_attributes:
                                if len(pos_attr) == 2:
                                    pos_type =  pos_attr[0]
                                    pos_size = int(pos_attr[1])
                                    if pos_size <= -1:
                                        found = True
                                        pos_attributes[pos_type] = pos_size
                                    style_item['css_attr_' + pos_type] = pos_size
                        items.append(style_item)

                        #if a potentially malicious class was found, look for
                        #elements using that class and extract any iframes out of it
                        if found == True or hidden == True:
                            matches_by_class = sel.css(css_class[0])
                            for match in matches_by_class:
                                raw_str = match.extract()
                                if "iframe" in raw_str:
                                    iframe_matches = match.xpath("iframe")
                                    for iframe_match in iframe_matches:
                                        raw_iframe = iframe_match.extract()
                                        item2 = PageLink()

                                        item2['tag_name'] = 'iframe'
                                        # raw tag
                                        item2['raw'] = raw_str

                                        # src attribute
                                        tag_src = iframe_match.xpath("@src").extract()
                                        if tag_src and len(tag_src) == 1:
                                            item2['uri'] = tag_src[0]

                                        # 'width' attribute
                                        tag_width = iframe_match.xpath("@width").extract()
                                        if tag_width and len(tag_width) == 1:
                                            item2['attr_width'] = tag_width[0]

                                        # 'height' attribute
                                        tag_height = iframe_match.xpath("@height").extract()
                                        if tag_height and len(tag_height) == 1:
                                            item2['attr_height'] = tag_height[0]

                                        if hidden == True:
                                            item2['css_attr_visibility'] = 'hidden'

                                        for attr in pos_attributes:
                                            item2['css_attr_' + attr] = pos_attributes[attr]
                                        item2['css_class'] = css_class[0]

                                        items.append(item2)



        ###### Parse <a> tags, extract 'href' and 'text'
        anchor_nodes = sel.xpath("//a")
        for node in anchor_nodes:
            item = PageLink()

            item['tag_name'] = 'a'
            # raw anchor tag
            item['raw'] = node.extract()
            # anchor 'text' attribute
            anchor_text = node.xpath("text()").extract()
            if anchor_text and len(anchor_text) == 1:
                item['attr_text'] = anchor_text[0]

            anchor_href = node.xpath("@href").extract()
            if anchor_href and len(anchor_href) == 1:
                item['uri'] = anchor_href[0]

            items.append(item)

        ###### Parse <link> tags, extract 'href' and 'type'
        link_nodes = sel.xpath("//link")
        for node in link_nodes:
            item = PageLink()

            item['tag_name'] = 'link'
            # raw link tag
            item['raw'] = node.extract()
            # link 'href' attribute
            link_href = node.xpath("@href").extract()
            if link_href and len(link_href) == 1:
                item['uri'] = link_href[0]

            # link 'type' attribute
            link_type = node.xpath("@type").extract()
            if link_type and len(link_type) == 1:
                item['attr_type'] = link_type[0]

            items.append(item)

        ###### Parse <object> tags, extract 'data', 'width', and 'height'
        object_nodes = sel.xpath("//object")
        for node in object_nodes:
            item = PageLink()

            item['tag_name'] = 'object'
            # raw object tag
            item['raw'] = node.extract()

            # object 'data' attribute
            object_data = node.xpath("@data").extract()
            if object_data and len(object_data) == 1:
                item['uri'] = object_data[0]

            # object 'width' attribute
            object_width = node.xpath("@width").extract()
            if object_width and len(object_width) == 1:
                item['attr_width'] = object_width[0]

            # object 'height' attribute
            object_height = node.xpath("@height").extract()
            if object_height and len(object_height) == 1:
                item['attr_height'] = object_height

            items.append(item)

        ###### Parse common list of tags and extract 'src', 'width', and 'height'
        tag_list_one = ['embed','frame','iframe','img','input','video']
        for tag in tag_list_one:
            tag_nodes = sel.xpath("//"+tag)
            for node in tag_nodes:
                item = PageLink()

                #TODO:  move this into a separate function
                #check for style info, particular things like "position: absolute; top: -10px, left: -10px;"
                style_tag = node.xpath("@style").extract()
                hidden = False
                if style_tag and len(style_tag) == 1:
                    css_position = LinkParser.re_css_position.search(style_tag[0])
                    css_position_attributes = LinkParser.re_css_position_attributes.findall(style_tag[0])
                    css_hidden_visibility = LinkParser.re_css_hidden_visibility.findall(style_tag[0])
                    if len(css_hidden_visibility) > 0:
                        hidden = True
                    if css_position is not None and css_position_attributes is not None:
                        for pos_attr in css_position_attributes:
                            if len(pos_attr) == 2:
                                pos_type =  pos_attr[0]
                                pos_size = int(pos_attr[1])
                                if pos_size <= -1:
                                    item['css_attr_' + pos_type] = pos_size

                item['tag_name'] = tag
                # raw tag
                item['raw'] = node.extract()

                # src attribute
                tag_src = node.xpath("@src").extract()
                if tag_src and len(tag_src) == 1:
                    item['uri'] = tag_src[0]

                # 'width' attribute
                tag_width = node.xpath("@width").extract()
                if tag_width and len(tag_width) == 1:
                    item['attr_width'] = tag_width[0]

                # 'height' attribute
                tag_height = node.xpath("@height").extract()
                if tag_height and len(tag_height) == 1:
                    item['attr_height'] = tag_height[0]

                if hidden == True:
                    item['css_attr_visibility'] = 'hidden'

                items.append(item)

        ###### Parse common list of tags and extract only 'src' attribute
        tag_list_two = ['audio','script','source','track']
        for tag in tag_list_two:
            tag_nodes = sel.xpath("//"+tag)
            for node in tag_nodes:
                item = PageLink()

                item['tag_name'] = tag
                # raw tag
                item['raw'] = node.extract()

                # src attribute
                tag_src = node.xpath("@src").extract()
                if tag_src and len(tag_src) == 1:
                    item['uri'] = tag_src[0]

                if tag == 'script':
                    language = node.xpath("@language").extract()
                    script_type = node.xpath("@type").extract()
                    if len(language) >= 1:
                        item['attr_language'] = language[0]

                    if len(script_type) >= 1:
                        item['attr_script_type'] = script_type[0]

                items.append(item)

        ###### Parse common list of tags and extract only 'href' attribute
        tag_list_three = ['area','base']
        for tag in tag_list_three:
            tag_nodes = sel.xpath("//"+tag)
            for node in tag_nodes:
                item = PageLink()

                item['tag_name'] = tag
                # raw tag
                item['raw'] = node.extract()

                # href attribute
                tag_href = node.xpath("@href").extract()
                if tag_href and len(tag_href) == 1:
                    item['uri'] = tag_href[0]

                items.append(item)

        # return array of items
        return items

    @staticmethod
    def get_page_data(response):
        page = WebPage()
        page['uri'] = response.url
        page['status_code'] = response.status

        if 'screenshot' in response.meta:
            page['screenshot'] = response.meta['screenshot']
            page['ssdeep_pagesource'] = str(ssdeep.hash(response.body))

            try:
                screenshot_hash = ssdeep.hash_from_file(response.meta['screenshot'])
                page['ssdeep_screenshot'] = screenshot_hash
            except:
                log.msg("Could not create hash from screenshot: " + response.meta['screenshot'], level=log.DEBUG)

        return page
