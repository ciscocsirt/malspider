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

from scrapy.http import Request, TextResponse
from selenium.webdriver.common.action_chains import ActionChains


class WebdriverRequest(Request):
    """A Request needed when using the webdriver download handler."""
    WAITING = None

    def __init__(self, url, manager=None, **kwargs):
        super(WebdriverRequest, self).__init__(url, **kwargs)
        self.manager = manager

    def replace(self, *args, **kwargs):
        kwargs.setdefault('manager', self.manager)
        return super(WebdriverRequest, self).replace(*args, **kwargs)


class WebdriverActionRequest(WebdriverRequest):
    """A Request that handles in-page webdriver actions (action chains)."""
    def __init__(self, response, actions=None, **kwargs):
        kwargs.setdefault('manager', response.request.manager)
        url = kwargs.pop('url', response.request.url)
        super(WebdriverActionRequest, self).__init__(url, **kwargs)
        self._response = response
        self.actions = actions or response.actions
        self.parent = response.request

    def replace(self, *args, **kwargs):
        kwargs.setdefault('response', self._response)
        kwargs.setdefault('actions', self.actions)
        return super(WebdriverActionRequest, self).replace(*args, **kwargs)


class WebdriverResponse(TextResponse):
    """A Response that will feed the webdriver page into its body."""
    def __init__(self, url, webdriver, **kwargs):
        kwargs.setdefault('body', webdriver.page_source)
        kwargs.setdefault('encoding', 'utf-8')
        super(WebdriverResponse, self).__init__(url, **kwargs)
        self.actions = ActionChains(webdriver)
        self.webdriver = webdriver

    def action_request(self, **kwargs):
        """Return a Request object to perform the recorded actions."""
        kwargs.setdefault('meta', self.meta)
        return WebdriverActionRequest(self, **kwargs)
