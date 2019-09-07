# -*- coding: utf-8 -*-
import scrapy
import re

class RentSpider(scrapy.Spider):
    name = 'rent'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://sh.lianjia.com/zufang/jingan/']

    # 获取各区域的url并且发送请求
    def parse(self, response):
        # 获取各区url
        url_list = response.xpath("//div[@id='filter']/ul[2]/li/a/@href").extract()
        for url in url_list[1:]:
            # url补全
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                callback=self.parse_total_page
            )
     # 取得最大页数
    def parse_total_page(self,response):
        pat = re.compile(r'data-totalPage=(\d+)')
        totalpage = pat.findall(response.text)[0]
        for i in range(1,int(totalpage)+1):
            url = (response.url + 'pg{}/').format(i)
            yield scrapy.Request(
                url,
                callback=self.parse_rent_list
            )

    # 解析房屋列表
    def parse_rent_list(self,response):
        rent_list = response.xpath("//div[@class='content__article']/div[@class='content__list']/div")
        for rent in rent_list:
            item = {}
            item['title'] = rent.xpath("./a/@title").extract_first()
            item['detail_url'] = response.urljoin(rent.xpath("./a/@href").extract_first())
            item['area'] = response.url.split("/")[-2]
            yield scrapy.Request(
                item['detail_url'],
                callback=self.parse_detail,
                meta={'item':item}
            )

    # 取详情页
    def parse_detail(self,response):
        item = response.meta['item']
        item['price'] = response.xpath("//p[@class='content__aside--title']/span/text()").extract_first()
        item['huxing'] = response.xpath("//p[@class='content__article__table']/span[2]/text()").extract_first()
        item['area'] = response.xpath("//p[@class='content__article__table']/span[3]/text()").extract_first()
        item['trafic'] = response.xpath("//div[@id='around']/ul/li/span[1]/text()").extract()
        item['distance'] = response.xpath("//div[@id='around']/ul/li/span[2]/text()").extract()
        yield item



