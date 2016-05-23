# -*- coding: utf-8 -*-

BOT_NAME = 'full_domain'

SPIDER_MODULES = ['malspider.spiders']
NEWSPIDER_MODULE = 'malspider.spiders'

LOG_FILE='spider.log'

#Handle ALL HTTP status codes, including those that are not valid (outside the 200-300 range)
HTTPERROR_ALLOW_ALL = True

REDIRECT_ENABLED = False

ROBOTSTXT_OBEY = True

#default useragent
USER_AGENT = 'Mozilla/5.0 (Android; Tablet; rv:30.0) Gecko/30.0 Firefox/30.0'

ITEM_PIPELINES = {
        'malspider.pipelines.DuplicateFilterPipeline': 800,
        'malspider.pipelines.MySQLPipeline':900,
}

#screenshots
TAKE_SCREENSHOT = False
SCREENSHOT_LOCATION = '<full_file_path>'


DOWNLOAD_HANDLERS = {
        'http': 'malspider.scrapy_webdriver.download.WebdriverDownloadHandler',
        'https': 'malspider.scrapy_webdriver.download.WebdriverDownloadHandler',
}

DOWNLOADER_MIDDLEWARES = {
        'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
        'malspider.middlewares.random_useragent.RandomUserAgentMiddleware': 100,
        'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': 200,
}

SPIDER_MIDDLEWARES = {
        'malspider.scrapy_webdriver.middlewares.WebdriverSpiderMiddleware': 543,
}

DRIVER_WINDOW_WIDTH = 1380
DRIVER_WINDOW_HEIGHT = 720

WEBDRIVER_BROWSER = 'PhantomJS'  # Or any other from selenium.webdriver

# Optional passing of parameters to the webdriver
WEBDRIVER_OPTIONS = {
                'service_args': ['--debug=true', '--load-images=true', '--webdriver-loglevel=debug']
#                'service_args': ['--debug=true', '--load-images=true', '--webdriver-loglevel=debug', '--proxy=<address>','--proxy-type=<http,sock5,etc>']

}

### DATABASE ###
MYSQL_HOST = 'localhost'
MYSQL_DB = 'malspider'
MYSQL_USER = '<username>'
MYSQL_PASSWORD = '<password>'
