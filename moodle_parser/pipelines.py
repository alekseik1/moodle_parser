# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from moodle_parser.spiders.grades_spider import GradesSpider


class SetTaskType:

    KNOWN_TYPES = {'quiz', 'assign'}
    
    @classmethod
    def get_type(cls, url):
        for i in cls.KNOWN_TYPES:
            if i in url:
                return i
        return 'unknown'

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if isinstance(spider, GradesSpider):
            adapter['task_type'] = self.get_type(adapter['url'])
        return item


class DropAssignTasks:
    def process_item(self, item, spider):
        if isinstance(spider, GradesSpider):
            # Их не надо катать
            if item.get('task_type') == 'assign':
                raise DropItem()
        return item
