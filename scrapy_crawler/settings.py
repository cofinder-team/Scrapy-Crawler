import os

BOT_NAME = "scrapy_crawler"
SPIDER_MODULES = [
    "scrapy_crawler.Joonggonara.TotalSearch.spiders",
    "scrapy_crawler.Bungae.TotalSearch.spiders",
    "scrapy_crawler.DBWatchDog.SoldOut.spiders",
    "scrapy_crawler.DBWatchDog.Classify.spiders",
    "scrapy_crawler.DBWatchDog.DailyScheduler.spiders.PriceUpdateSpider",
    "scrapy_crawler.Daangn.spiders.DaangnMetaSpider",
]
NEWSPIDER_MODULE = "scrapy_crawler.Joonggonara.TotalSearch.spiders"

# ENV
SCRAPEOPS_API_KEY = os.environ.get("SCRAPEOPS_API_KEY")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_DATABASE = os.environ.get("DB_DATABASE")
SLACK_BOT_LABELING_TOKEN = os.environ.get("SLACK_BOT_LABELING_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "scrapy_crawler (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

DOWNLOAD_DELAY = 2

CONCURRENT_REQUESTS_PER_DOMAIN = 16

CONCURRENT_REQUESTS_PER_IP = 16

COOKIES_ENABLED = True

TELNETCONSOLE_ENABLED = False

# Log level
LOG_LEVEL = "INFO"
SPIDER_MIDDLEWARES = {
    "scrapy.spidermiddlewares.referer.RefererMiddleware": None,
}

DOWNLOADER_MIDDLEWARES = {
    "scrapeops_scrapy.middleware.retry.RetryMiddleware": 550,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
}

EXTENSIONS = {
    "scrapeops_scrapy.extension.ScrapeOpsMonitor": 500,
}

RETRY_ENABLED = True

RETRY_TIMES = 2

RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

HTTPERROR_ALLOWED_CODES = [404]

HTTPERROR_ALLOW_ALL = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
