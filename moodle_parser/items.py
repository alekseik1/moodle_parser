# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class Task(scrapy.Item):
    name = Field()
    url = Field()
    task_type = Field()
    task_id = Field()
    grade = Field()
    max_grade = Field()
