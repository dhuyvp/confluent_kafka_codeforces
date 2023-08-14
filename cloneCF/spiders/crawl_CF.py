#!/usr/bin/env python

from cloneCF.settings import KAFKA_BROKERS, KAFKA_TOPIC
import scrapy
from cloneCF.items import UserInfoItem
from confluent_kafka import Producer

def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: user_name = {user_name}".format(
                topic=msg.topic(), user_name=msg.value() )
            )


class CrawlCfSpider(scrapy.Spider):
    name = "crawl_CF"
    allowed_domains = ["codeforces.com"]
    start_urls = [
        "https://codeforces.com/ratings/"
    ]

    custom_settings = {
        'FEEDS' : {
            'userdata.json' : {'format' : 'json', 'overwrite' : True},
        }
    }

    def parse(self, response):
        users = response.xpath("//table[@class='']/tr/td").css("a::attr(href)")

        print(len(users))

        for user in users :
            relate_url =  user.get()

            if relate_url is not None  and 'profile' in relate_url :
                if relate_url[0] == "/" :
                    user_url = "https://codeforces.com" + relate_url
                else :
                    user_url = "https://codeforces.com/" + relate_url

                yield response.follow(user_url, callback = self.parse_user_info)


        next_page = response.xpath("//div[@class='pagination']/ul/li")[-1].css('a::attr(href)').get()
        
        if next_page is not None and '2' not in next_page:
            if next_page[0] == '/' : 
                next_page_url = "https://codeforces.com" + next_page
            else :
                next_page_url = "https://codeforces.com/" + next_page

            yield {
                'next_page' : next_page_url,
            }

            yield response.follow(next_page_url, callback = self.parse)

    def parse_user_info(self, response) :
        class_list = ['main-info']    
        divs = response.xpath('//div[contains(@class, "{}")]'.format(' | '.join(class_list)))
        user_name = divs.xpath("//h1/a/@href").get().split('/')[-1]

        userInfo = UserInfoItem()
        
        userInfo['user_name'] = response.xpath('//div[contains(@class, "{}")]'.format(' | '.join(class_list))).xpath("//h1/a/@href").get().split('/')[-1]
        userInfo['current_rank'] = response.xpath("//div[@class='user-rank']/span/text()").get()
        userInfo['contests'] = ""
        userInfo['comments'] = []
        yield response.follow('https://codeforces.com/comments/with/tourist', callback=self.parse_comments, cb_kwargs={'userInfo':userInfo})

        # parse_contests(self, userInfo, response)
        # contests_url = response.xpath("//div[@id='pageContent']/div/ul/li/a/@href")[-2].get()

        # producer.produce(topic, userInfo, callback=delivery_callback)
        producer = Producer({
            'bootstrap.servers': KAFKA_BROKERS,
            # 'client.id': 'my-producer',
        })

        producer.produce(
            topic="codeforces",
            key=userInfo['user_name'],
            value=userInfo['current_rank'],
            # userInfo=userInfo,
            callback=delivery_callback
        )

        producer.flush()

        yield userInfo

    def parse_comments(self, response, userInfo) :
        userInfo['comments'].append(1)

        print('user name: ', userInfo['user_name'], '\n\n')

        yield userInfo

    def parse_contests(self, response) :
        yield "ass"