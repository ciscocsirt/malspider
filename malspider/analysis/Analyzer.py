#  
#  Copyright (c) 2016-present, Cisco Systems, Inc. All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. 
#
from .BaseAnalyzer import BaseAnalyzer
from malspider.analysis.URLClassifier import URLClassifier
from malspider.analysis.HTMLClassifier import HTMLClassifier
from malspider.analysis.JSClassifier import JSClassifier

class Analyzer(BaseAnalyzer):
    def __init__(self, response):
        BaseAnalyzer.__init__(self,response)

    def inspect_response(self):
        all_alerts = list()
        all_alerts += filter(None, self.url_scan())
        all_alerts += filter(None, self.html_scan())
        all_alerts += filter(None, self.js_scan())
        all_alerts += filter(None, self.get_hidden_elems())
        return all_alerts

    # yara scan against links 
    def url_scan(self):
        alerts = []
        for elem in self.src_attr_elems:
            raw = elem.extract()
            uri = elem.xpath('@src').extract()[0]
            scan_results = URLClassifier.scan(uri)
            for result in scan_results:
                alerts.append(self.gen_alert(result[0],raw, result[1]))
        return alerts

    # yara scan against html body
    def html_scan(self):
        alerts = []
        scan_results = HTMLClassifier.scan(self.response.body)
        for result in scan_results:
                alerts.append(self.gen_alert(result[0],self.response.body, result[1]))
        return alerts       
   
    # yara scan against javascript
    # currently only supports inline scripts
    def js_scan(self):
        alerts = []
        script_elems = self.dom_parser.extract_script_elems()
        for elem in script_elems:
            raw = elem.extract()
            scan_results = JSClassifier.scan(raw)
            for result in scan_results:
                alerts.append(self.gen_alert(result[0],raw, result[1]))
        return alerts

    # get 0x0 pixel elements and elements hidden using css obfuscation 
    def get_hidden_elems(self):
        alerts = []
        hidden_elems = self.dom_parser.extract_hidden_elements()
        if not hidden_elems is None:
            for item in hidden_elems:
                resource = item[0]
                raw = item[1]
                elem = item[2]
                reason = "Hidden Element <%s>" % (elem.xpath("name()").extract()[0])
                alert = self.gen_alert(reason,raw,resource)
                alerts.append(alert)
        return alerts
