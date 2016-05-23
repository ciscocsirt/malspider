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

from scrapy.exceptions import IgnoreRequest, NotConfigured

from .http import WebdriverActionRequest, WebdriverRequest
from .manager import WebdriverManager


class WebdriverSpiderMiddleware(object):
    """This middleware coordinates concurrent webdriver access attempts."""
    def __init__(self, crawler):
        self.manager = WebdriverManager(crawler)

    @classmethod
    def from_crawler(cls, crawler):
        try:
            return cls(crawler)
        except Exception as e:
            raise NotConfigured('WEBDRIVER_BROWSER is misconfigured: %r (%r)'
                % (crawler.settings.get('WEBDRIVER_BROWSER'), e))

    def process_start_requests(self, start_requests, spider):
        """Return start requests, with some reordered by the manager.

        The reordering occurs as a result of some requests waiting to gain
        access to the webdriver instance. Those waiting requests are queued up
        in the manager, from which we pop the next in line after we release the
        webdriver instance while processing spider output.

        """
        return self._process_requests(start_requests, start=True)

    def process_spider_output(self, response, result, spider):
        """Return spider result, with some requests reordered by the manager.

        See ``process_start_requests`` for a description of the reordering.

        """
        for item_or_request in self._process_requests(result):
            yield item_or_request
        if isinstance(response.request, WebdriverRequest):
            # We are here because the current request holds the webdriver lock.
            # That lock was kept for the entire duration of the response
            # parsing callback to keep the webdriver instance intact, and we
            # now release it.
            self.manager.release(response.request.url)
            next_request = self.manager.acquire_next()
            if next_request is not WebdriverRequest.WAITING:
                yield next_request.replace(dont_filter=True)

    def _process_requests(self, items_or_requests, start=False):
        """Acquire the webdriver manager when it's available for requests."""
        error_msg = "WebdriverRequests from start_requests can't be in-page."
        for request in iter(items_or_requests):
            if isinstance(request, WebdriverRequest):
                if start and isinstance(request, WebdriverActionRequest):
                    raise IgnoreRequest(error_msg)
                request = self.manager.acquire(request)
                if request is WebdriverRequest.WAITING:
                    continue  # Request has been enqueued, so drop it.
            yield request
