import os
import scrapy
from dotenv import load_dotenv
load_dotenv()


class AuthBaseSpider(scrapy.Spider):
    """
    От этого класса нужно отнаследоваться, потом переопределить `after_login()` с ОБЯЗАТЕЛЬНЫМ
    вызовом `super().after_login(self, response, **kwargs)`.
    После этого можно ходить на мудл, будучи авторизованным
    """
    allowed_domains = ['moodle.phystech.edu']
    start_urls = ['http://moodle.phystech.edu/login/index.php']

    @staticmethod
    def authentication_failed(response):
        return response.css('span.error::text').get() is not None

    def parse(self, response, **kwargs):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'username': os.environ.get('MOODLE_LOGIN'),
                'password': os.environ.get('MOODLE_PASSWORD')},
            callback=self.after_login)

    def after_login(self, response, **kwargs):
        if self.authentication_failed(response):
            self.logger.error("Login failed")
            return
