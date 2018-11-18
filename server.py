import tornado.ioloop
import tornado.web
from db import *
import os

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = db_session()

    def on_finish(self):
        self.session.close()


class IndexHandler(BaseHandler):
    def get(self, *args, **kwargs):
        topics = self.session.query(Topic).all()
        self.render("index.html", title="title",topics=topics)

settings = dict(
            blog_title=u"Tornado Blog",
            template_path=os.path.join(os.path.dirname(__file__), "tpl"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
            autoreload=False
        )


def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()