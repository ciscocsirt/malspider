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

#import time

from scrapy import log, version_info
from scrapy.utils.decorator import inthread
from scrapy.utils.misc import load_object

from random import randint
from malspider import settings

from .http import WebdriverActionRequest, WebdriverRequest, WebdriverResponse

if map(int, version_info) < [0, 18]:
    FALLBACK_HANDLER = 'http.HttpDownloadHandler'
elif map(int, version_info) >= [0, 24, 4]:
    FALLBACK_HANDLER = 'http.HTTPDownloadHandler'
else:
    FALLBACK_HANDLER = 'http10.HTTP10DownloadHandler'
FALLBACK_HANDLER = 'scrapy.core.downloader.handlers.%s' % FALLBACK_HANDLER


class WebdriverDownloadHandler(object):
    """This download handler uses webdriver, deferred in a thread.

    Falls back to the stock scrapy download handler for non-webdriver requests.

    """
    def __init__(self, settings):
        self._enabled = settings.get('WEBDRIVER_BROWSER') is not None
        self._fallback_handler = load_object(FALLBACK_HANDLER)(settings)

    def download_request(self, request, spider):
        """Return the result of the right download method for the request."""
        if self._enabled and isinstance(request, WebdriverRequest):
            if isinstance(request, WebdriverActionRequest):
                download = self._do_action_request
            else:
                download = self._download_request
        else:
            download = self._fallback_handler.download_request
        return download(request, spider)

    @inthread
    def _download_request(self, request, spider):
        """Download a request URL using webdriver."""
        log.msg('Downloading %s with webdriver' % request.url, level=log.DEBUG)
        request.manager.webdriver.get(request.url)
        #time.sleep(5)
        take_screenshot = getattr(settings, 'TAKE_SCREENSHOT', None)
        screenshot_loc = getattr(settings, 'SCREENSHOT_LOCATION', None)
        if take_screenshot and screenshot_loc:
          screenshot_location = screenshot_loc + str(randint(10000,10000000)) + '.png'
          request.manager.webdriver.save_screenshot(screenshot_location)
          request.meta['screenshot'] = screenshot_location

        request.meta['User-Agent'] = request.headers.get('User-Agent')
        request.meta['Referer'] = request.headers.get('Referer')
        return WebdriverResponse(request.url, request.manager.webdriver)

    @inthread
    def _do_action_request(self, request, spider):
        """Perform an action on a previously webdriver-loaded page."""
        log.msg('Running webdriver actions %s' % request.url, level=log.DEBUG)
        request.actions.perform()
        return WebdriverResponse(request.url, request.manager.webdriver)
