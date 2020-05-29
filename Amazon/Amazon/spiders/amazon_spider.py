# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import AmazonItem


def clean(string):
    result = list()
    for i in string:
        result.append(re.sub(" +|\n|\r|\t|\0|\x0b|\xa0", ' ', i).strip())
    return result


class AmazonSpider(scrapy.Spider):
    name = 'amazon_spider'

    def __init__(self, category='', **kwargs):
        self.start_urls = [f'https://www.amazon.in/s?k={category}&rh=p_72%3A1318476031&s=price-asc-rank']
        super().__init__(**kwargs)

    custom_settings = {'FEED_URI': 'Amazon/outputfile.json', 'CLOSESPIDER_TIMEOUT': 15}

    def parse(self, response):
        links = response.css('.a-color-base a.a-text-normal').css('::attr(href)').extract()
        # yield response.follow(links[0], callback=self.get_details)
        for i in links:
            self.url = 'https://www.amazon.in/' + i
            yield response.follow(i, callback=self.get_details)

    def get_details(self, response):
        product_detail = AmazonItem()
        name = response.css('#productTitle::text').extract()
        description = response.css('#feature-bullets .a-list-item').css('::text').extract()
        price = response.css('#priceblock_ourprice::text').extract()
        image_link = response.css('#imgTagWrapperId img').css('::attr(data-old-hires)').extract()
        link = response.url

        product_detail['product_name'] = clean(name)
        product_detail['product_description'] = clean(description)
        if price:
            product_detail['product_price'] = price[0].replace(u'\xa0', u' ')
            product_detail['product_availability'] = 'Available'
        else:
            product_detail['product_price'] = '0/-'
            product_detail['product_availability'] = 'Not Available'
        product_detail['product_link'] = link
        product_detail['product_image_link'] = image_link
        yield product_detail
