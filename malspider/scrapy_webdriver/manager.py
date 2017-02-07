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


import inspect
from collections import deque
from threading import Lock

from scrapy.signals import engine_stopped
from .http import WebdriverRequest, WebdriverActionRequest
from selenium import webdriver
from malspider import settings


class WebdriverManager(object):
    """Manages the life cycle of a webdriver instance."""
    USER_AGENT_KEY = 'phantomjs.page.settings.userAgent'

    def __init__(self, crawler):
        self.crawler = crawler
        self._lock = Lock()
        self._wait_queue = deque()
        self._wait_inpage_queue = deque()
        self._browser = crawler.settings.get('WEBDRIVER_BROWSER', None)
        self._user_agent = crawler.settings.get('USER_AGENT', None)
        self._options = crawler.settings.get('WEBDRIVER_OPTIONS', dict())
        self._webdriver = None
        if isinstance(self._browser, basestring):
            if '.' in self._browser:
                module, browser = self._browser.rsplit('.', 2)
            else:
                module, browser = 'selenium.webdriver', self._browser
            module = __import__(module, fromlist=[browser])
            self._browser = getattr(module, browser)
        elif inspect.isclass(self._browser):
            self._browser = self._browser
        else:
            self._webdriver = self._browser

    @property
    def _desired_capabilities(self):
        capabilities = dict()
        if self._user_agent is not None:
            capabilities[self.USER_AGENT_KEY] = self._user_agent
        return capabilities or None

    @property
    def webdriver(self):
        """Return the webdriver instance, instantiate it if necessary."""
        if self._webdriver is None:
            short_arg_classes = (webdriver.Firefox, webdriver.Ie)
            if issubclass(self._browser, short_arg_classes):
                cap_attr = 'capabilities'
            else:
                cap_attr = 'desired_capabilities'
            options = self._options
            options[cap_attr] = self._desired_capabilities
            self._webdriver = self._browser(**options)
            self._webdriver.set_window_size(settings.DRIVER_WINDOW_WIDTH, settings.DRIVER_WINDOW_HEIGHT)
            self._webdriver.set_page_load_timeout(self.crawler.settings.get('DOMAIN_TIMEOUT', 30))
            self.crawler.signals.connect(self._cleanup, signal=engine_stopped)
        return self._webdriver

    def acquire(self, request):
        """Acquire lock for the request, or enqueue request upon failure."""
        assert isinstance(request, WebdriverRequest), \
            'Only a WebdriverRequest can use the webdriver instance.'
        if self._lock.acquire(False):
            request.manager = self
            return request
        else:
            if isinstance(request, WebdriverActionRequest):
                queue = self._wait_inpage_queue
            else:
                queue = self._wait_queue
            queue.append(request)

    def acquire_next(self):
        """Return the next waiting request, if any.

        In-page requests are returned first.

        """
        try:
            request = self._wait_inpage_queue.popleft()
        except IndexError:
            try:
                request = self._wait_queue.popleft()
            except IndexError:
                return
        return self.acquire(request)

    def release(self, msg):
        """Release the the webdriver instance's lock."""
        self._lock.release()

    def _cleanup(self):
        """Clean up when the scrapy engine stops."""
        if self._webdriver is not None:
            self._webdriver.quit()
            assert len(self._wait_queue) + len(self._wait_inpage_queue) == 0, \
                'Webdriver queue not empty at engine stop.'
