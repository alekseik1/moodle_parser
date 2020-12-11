from itemloaders.processors import MapCompose
from scrapy.loader import ItemLoader
from moodle_parser.spiders.common import AuthBaseSpider
from moodle_parser.items import Attempt


class TaskFieldsSpider(AuthBaseSpider):
    name = 'task_fields_spider'

    def __init__(self, task_id: int):
        super().__init__()
        self.task_id = task_id

    def after_login(self, response, **kwargs):
        super().after_login(response, **kwargs)
        # Теперь идем за курсами
        yield response.follow(f'/mod/quiz/view.php?id={self.task_id}', callback=self.parse_summary)

    def parse_summary(self, response, **kwargs):
        # Лучшая попытка прячется в классе bestrow
        row = response.css('tbody > tr.bestrow')
        loader = ItemLoader(Attempt(), response=response, selector=row)
        loader.add_css('details_link', 'td.lastcol > a::attr(href)')
        nested = loader.nested_css('td.lastcol')
        nested.add_xpath('mark', '(./preceding-sibling::*)[last()]/./text()',
                         MapCompose(lambda x: float(x.replace(',', '.'))))
        yield loader.load_item()

