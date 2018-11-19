import tornado.ioloop
import tornado.web
from db import *
import os
import json

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = db_session()

    def on_finish(self):
        self.session.close()

    def get_current_user(self):
        return self.get_secure_cookie("user")

    @property
    def is_auth(self):
        return True if self.get_current_user() else False


class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name:<input type="text" name="name"><br/>'
                   'Password:<input type="password" name="password"><br/>'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        name = self.get_argument("name")
        password = self.get_argument("password")
        user = self.session.query(User).filter(User.name==name).one()
        if user and user.password == password:
            self.set_secure_cookie("user", str(user.id))
            self.redirect("/")
        else:
            return self.write("login failed")


class IndexHandler(BaseHandler):
    def get(self, *args, **kwargs):
        topics = self.session.query(Topic).all()
        self.render("index.html", topics=topics)


class DetailHandler(BaseHandler):
    def get(self, id):
        topic = self.session.query(Topic).filter(Topic.id==id).one()
        self.render("detail.html", topic=topic)


class ReplyHandler(BaseHandler):
    def post(self):
        uid = self.get_current_user()
        tid = self.get_argument("id")
        data = self.get_argument("data")
        comment = self.session.query(Comment).filter(Comment.id==1).one()
        comment.content = data
        self.session.commit()
        self.write("success")


settings = dict(
            blog_title=u"Tornado Blog",
            template_path=os.path.join(os.path.dirname(__file__), "tpl"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            # xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
            autoreload=False
        )


def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/detail/(\d+)", DetailHandler),
        (r"/reply", ReplyHandler),
        (r"/login", LoginHandler)
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()