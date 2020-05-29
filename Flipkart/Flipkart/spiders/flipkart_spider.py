# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import FlipkartItem


def clean(string):
    result = list()
    for i in string:
        result.append(re.sub(" +|\n|\r|\t|\0|\x0b|\xa0", ' ', i).strip())
    return result


class FlipkartSpider(scrapy.Spider):
    name = 'flipkart_spider'

    def __init__(self, category=None, *args, **kwargs):
        super(FlipkartSpider, self).__init__(*args, **kwargs)
        self.url = 'https://www.flipkart.com/search?q='
        self.filters = '&sort=popularity&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove'
        self.start_urls = [f'{self.url}{category}{self.filters}']

    custom_settings = {'FEED_URI': 'Flipkart/outputfile.json', 'CLOSESPIDER_TIMEOUT': 15}

    def parse(self, response):
        links = response.css('._2cLu-l::attr(href)')[:3].extract()
        for i in links:
            self.url = 'https://www.flipkart.com/' + i
            yield response.follow(i, callback=self.get_details)

    def get_details(self, response):
        product_detail = FlipkartItem()
        name = response.css('._35KyD6::text').extract()
        description = response.css('.col.col-3-12 , ._3YhLQA').css('::text').extract()
        price = response.css('._3qQ9m1::text').extract()
        image_link = response.css('img ._1Nyybr .Yun65Y .OGBF1g ._30XEf0').css('::attr(src)').extract()
        link = response.url

        product_detail['product_name'] = clean(name)
        product_detail['product_description'] = clean(description)
        if not(response.css('._13J5uS')):
            product_detail['product_price'] = price[0].replace(u'\xa0', u' ')
            product_detail['product_availability'] = 'Available'
        else:
            product_detail['product_price'] = '0/-'
            product_detail['product_availability'] = 'Not Available'
        product_detail['product_link'] = link
        product_detail['product_image_link'] = image_link
        yield product_detail
