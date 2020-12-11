import os
import scrapy
from dotenv import load_dotenv
from scrapy.http import Response

from moodle_parser.items import Task

load_dotenv()


def authentication_failed(response, self):
    return response.css('span.error::text').get() is not None


class GradesSpider(scrapy.Spider):
    name = 'grades_spider'
    allowed_domains = ['moodle.phystech.edu']
    start_urls = ['http://moodle.phystech.edu/login/index.php']

    def parse(self, response, **kwargs):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'username': os.environ.get('MOODLE_LOGIN'),
                'password': os.environ.get('MOODLE_PASSWORD')},
            callback=self.after_login)

    def after_login(self, response):
        if authentication_failed(response, self):
            self.logger.error("Login failed")
            return
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
