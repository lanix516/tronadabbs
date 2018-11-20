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
        topics = self.session.query(Topic).offset(0).limit(10).all()
        self.render("index.html", topics=topics)


class DetailHandler(BaseHandler):
    def get(self, id):
        topic = self.session.query(Topic).filter(Topic.id==id).one()
        self.render("detail.html", topic=topic)


class PostTopicHandler(BaseHandler):
    def get(self):
        if not self.is_auth:
            self.redirect("/login")
        self.render("post.html")

    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        uid = int(self.get_current_user())
        print(self.get_current_user())
        topic = Topic(title=title, content=content, user_id=uid)
        self.session.add(topic)
        self.session.commit()
        self.redirect("/")


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
        (r"/post", PostTopicHandler),
        (r"/reply", ReplyHandler),
        (r"/login", LoginHandler)
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()