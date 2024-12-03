from src.db.database_handler import DataBaseHandler, Base
from src.util.image_processing import *
import sqlite3
import scrapy
from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess
from sqlalchemy import Column, Integer
from pathlib import Path


class Colors(Base):
    __tablename__ = "colors"

    ColorId = Column(Integer, primary_key=True)
    Gamma = Column(Integer)


class GammaHandler(DataBaseHandler):
    def __init__(self, sqlite_db_path: str):
        super().__init__(sqlite_db_path)


class ColorParserPipeline:
    def process_item(self, item, spider):
        return item


class ColormapItem(scrapy.Item):
    color_code = scrapy.Field()
    color_name = scrapy.Field()
    color_hex = scrapy.Field()


class ColorsSpider(scrapy.Spider):
    name = "colors"
    start_urls = ["https://firma-gamma.ru/articles/colormap-muline/"]

    def get_background_color(self, attr):
        styles = attr.split(';')
        for style in styles:
            if 'background-color' in style:
                return style.split(':')[1].strip()

    def parse(self, response):
        rows = response.xpath('//table//tr')
        elem = response.css('td[style]')
        i = 0
        for row in rows[1:]:
            i += 1
            row = rows[i]
            attr = elem[i].attrib.get('style', '')
            color = self.get_background_color(attr)
            item = ColormapItem()
            item['color_code'] = row.xpath('./td[1]//text()').get()
            item['color_name'] = row.xpath('./td[2]//text()').get()
            item['color_hex'] = color
            yield item


if __name__ == "__main__":
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json',
    }
    process = CrawlerProcess(settings=Settings(values=custom_settings))
    process.crawl(ColorsSpider)
    process.start()
