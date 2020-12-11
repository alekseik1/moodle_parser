from scrapy.http import Response

from moodle_parser.items import Task
from moodle_parser.spiders.common import AuthBaseSpider


class GradesSpider(AuthBaseSpider):
    name = 'grades_spider'

    def after_login(self, response, **kwargs):
        super().after_login(response, **kwargs)
        # Теперь идем за курсами
        yield response.follow('/grade/report/overview/index.php', callback=self.parse_first_course)

    def parse_first_course(self, response: Response):
        links = response.css('td.c0 > a::attr(href)').getall()
        yield from [response.follow(link, callback=self.parse_marks_page) for link in links]

    def parse_marks_page(self, response: Response):
        for task in response.css('tr > th > a.gradeitemheader'):
            yield Task(
                url=task.css('::attr(href)').get(),
                task_id=task.css('::attr(href)').re(r'[^r]id=(\d+)')[0],
                name=task.css('::text').get(),
                grade=task.xpath('parent::*/parent::*').css('.column-grade::text').get(),
                max_grade=task.xpath('parent::*/parent::*').css('.column-range::text').re_first(
                    r'–([\w\W]+)'),
            )
