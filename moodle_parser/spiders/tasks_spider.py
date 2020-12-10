import os
import scrapy
from dotenv import load_dotenv
from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.shell import inspect_response
from scrapy.spiders import CrawlSpider

from moodle_parser.items import Task

load_dotenv()


class GradesSpiderSpider(CrawlSpider):
    name = 'grades_spider'
    allowed_domains = ['moodle.phystech.edu']
    LOGIN_URL = 'http://moodle.phystech.edu/login/index.php'

    def start_requests(self):
        yield scrapy.Request(self.LOGIN_URL, callback=self.parse_login_token)

    def parse_login_token(self, response: Response, **kwargs):
        login_token = response.xpath('//input[@name="logintoken"]/@value').get()
        yield scrapy.FormRequest(
            response.url,
            formdata={
                'username': os.environ.get('MOODLE_LOGIN'),
                'password': os.environ.get('MOODLE_PASSWORD'),
                'anchor': '',
                'logintoken': login_token
            }, dont_filter=True, callback=self.parse_courses_page)

    def parse_courses_page(self, response: Response, **kwargs):
        yield scrapy.FormRequest(
            response.urljoin('/grade/report/overview/index.php'),
            callback=self.parse_first_course
        )

    def parse_first_course(self, response: Response, **kwargs):
        link = response.css('td.c0 > a::attr(href)').get()
        yield response.follow(link, callback=self.parse_marks_page)

    def parse_marks_page(self, response: Response, **kwargs):
        # inspect_response(response, self)
        for task in response.css('tr > th > a.gradeitemheader'):
            yield Task(
                url=task.css('::attr(href)').get(),
                name=task.css('::text').get(),
                grade=task.xpath('parent::*/parent::*//td[contains(@class, "column-grade")]/text()').get(),
                max_grade=task.xpath('parent::*/parent::*//td[contains(@class, "column-range")]/text()').re(
                    r'–([\w\W]+)')[0],
            )
