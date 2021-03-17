import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from mmvde.items import Article


class MmvdeSpider(scrapy.Spider):
    name = 'mmvde'
    start_urls = ['https://mmv.de/presse-aktuelles/page/1/']
    page = 1

    def parse(self, response):
        links = response.xpath('//a[@class="fusion-read-more"]/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)
            self.page += 1
            next_page = f'https://mmv.de/presse-aktuelles/page/{self.page}/'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.url[15:25]

        content = response.xpath('//div[@class="post-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
