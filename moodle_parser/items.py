# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field
from itemloaders.processors import TakeFirst, MapCompose


class Task(scrapy.Item):
    name = Field()
    url = Field()
    task_type = Field()
    task_id = Field()
    grade = Field()
    max_grade = Field()


class Attempt(scrapy.Item):
    mark = Field(output_processor=TakeFirst())
    details_link = Field(output_processor=TakeFirst())
