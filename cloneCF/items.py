# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ClonecfItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # user_name = scrapy.Field()
    pass

class UserInfoItem(scrapy.Item):
    user_name = scrapy.Field()
    current_rank = scrapy.Field()
    comments = scrapy.Field()
    # current_rate = scrapy.Field()
    # max_rank = scrapy.Field()
    # max_rate = scrapy.Field()
    # contribution = scrapy.Field()
    # num_of_friend = scrapy.Field()
    contests = scrapy.Field()
