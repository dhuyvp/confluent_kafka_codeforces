#!/usr/bin/env python

from cloneCF.settings import KAFKA_BROKERS, KAFKA_TOPIC
import scrapy
from cloneCF.items import UserInfoItem
from confluent_kafka import Producer
from datetime import datetime, timedelta

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
        # userInfo['contests'] = ""
        # userInfo['comments'] = []
        user_comments_url = 'https://codeforces.com/comments/with/' + str(userInfo['user_name'])

        yield response.follow(url=user_comments_url, callback=self.parse_comments, cb_kwargs={
            "userInfo": userInfo,
            })

        # parse_contests(self, userInfo, response)
        # contests_url = response.xpath("//div[@id='pageContent']/div/ul/li/a/@href")[-2].get()

        
        # yield userInfo

    def check_time(self, target_date_str) :
        target_date = datetime.strptime(target_date_str, "%b/%d/%Y %H:%M")

        # Calculate current time minus 5 minutes
        current_time = datetime.now()
        five_minutes_ago = current_time - timedelta(hours=24)

        # Compare the two datetime objects
        if target_date > five_minutes_ago:
            return True
        return False

    def parse_comments(self, response, **kwargs) :
        userInfo = UserInfoItem()
        userInfo['user_name'] = kwargs['userInfo']['user_name']
        userInfo['current_rank'] = kwargs['userInfo']['current_rank']
        userInfo['comments'] = []

        comments_divs = response.xpath('//div[@class="content-with-sidebar"]').css('div[style="margin:3em 1em;"]') 

        producer = Producer({
            'bootstrap.servers': KAFKA_BROKERS,
            # 'client.id': 'my-producer',
        })

        for id in range(len(comments_divs) ) :
            cmt = {
                'link': "https://codeforces.com/"+ comments_divs[id].css('a::attr(href)').extract()[3],
                'contest' : comments_divs[id].css('a::text').extract()[4],
                # 'datetime': comments_divs[id].css('.format-humantime::text').get()
                'datetime': comments_divs[id].css('.format-humantime::attr(title)').get(),
            }
            userInfo['comments'].append(cmt)

            if self.check_time(cmt['datetime']) :
                str_message = f"{userInfo['user_name']} commented on {cmt['contest']} contest's blog on {cmt['datetime']}. \nhref: {cmt['link']}"
                
                producer.produce(
                    topic="codeforces",
                    key=userInfo['user_name'],
                    value=str_message,
                    # userInfo=userInfo,
                    callback=delivery_callback
                )

                producer.flush()

            else :
                break

        yield userInfo

    def parse_contests(self, response) :
        yield "ass"