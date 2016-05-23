# Copyright (c) 2013 Nicolas Cadou, Sosign Interactive
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import re

try:
    from scrapy.selector import Selector, XPathSelectorList
except ImportError:  # scrapy < 0.20
    from scrapy.selector import XPathSelector as Selector, XPathSelectorList

_UNSUPPORTED_XPATH_ENDING = re.compile(r'.*/((@)?([^/()]+)(\(\))?)$')


class WebdriverXPathSelector(Selector):
    """Scrapy selector that works using XPath selectors in a remote browser.

    Based on some code from Marconi Moreto:
        https://github.com/marconi/ghost-selector

    """
    def __init__(self, response=None, webdriver=None, element=None,
                 *args, **kwargs):
        kwargs['response'] = response
        super(WebdriverXPathSelector, self).__init__(*args, **kwargs)
        self.response = response
        self.webdriver = webdriver or response.webdriver
        self.element = element

    def _make_result(self, result):
        if type(result) is not list:
            result = [result]
        return [self.__class__(webdriver=self.webdriver, element=e)
                for e in result]

    def select(self, xpath):
        """Return elements using the webdriver `find_elements_by_xpath` method.

        Some XPath features are not supported by the webdriver implementation.
        Namely, selecting text content or attributes:
          - /some/element/text()
          - /some/element/@attribute

        This function offers workarounds for both, so it should be safe to use
        them as you would with HtmlXPathSelector for simple content extraction.

        """
        xpathev = self.element if self.element else self.webdriver
        ending = _UNSUPPORTED_XPATH_ENDING.match(xpath)
        atsign = parens = None
        if ending:
            match, atsign, name, parens = ending.groups()
            if atsign:
                xpath = xpath[:-len(name) - 2]
            elif parens and name == 'text':
                xpath = xpath[:-len(name) - 3]
        result = self._make_result(xpathev.find_elements_by_xpath(xpath))
        if atsign:
            result = (_NodeAttribute(r.element, name) for r in result)
        elif parens and result and name == 'text':
            result = (_TextNode(self.webdriver, r.element) for r in result)
        return XPathSelectorList(result)

    def select_script(self, script, *args):
        """Return elements using JavaScript snippet execution."""
        result = self.webdriver.execute_script(script, *args)
        return XPathSelectorList(self._make_result(result))

    def extract(self):
        """Extract text from selenium element."""
        return self.element.text if self.element else None


class _NodeAttribute(object):
    """Works around webdriver XPath inability to select attributes."""
    def __init__(self, element, attribute):
        self.element = element
        self.attribute = attribute

    def extract(self):
        return self.element.get_attribute(self.attribute)


class _TextNode(object):
    """Works around webdriver XPath inability to select text nodes.

    It's a rather contrived element API implementation, it should probably
    be expanded.

    """
    JS_FIND_FIRST_TEXT_NODE = ('return arguments[0].firstChild '
                               '&& arguments[0].firstChild.nodeValue')

    def __init__(self, webdriver, element):
        self.element = element
        self.webdriver = webdriver

    def extract(self):
        args = (self.JS_FIND_FIRST_TEXT_NODE, self.element)
        return self.webdriver.execute_script(*args)
