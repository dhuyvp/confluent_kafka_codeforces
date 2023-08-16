import scrapy


class CrawlcfstatusSpider(scrapy.Spider):
    name = "crawlCFStatus"
    allowed_domains = ["codeforces.com"]
    start_urls = ["https://codeforces.com/problemset/status"]

    custom_settings = {
        'FEEDS' : {
            'CFStatus.json' : {'format' : 'json', 'overwrite' : True},
        }
    }

    def parse(self, response):
        pass
