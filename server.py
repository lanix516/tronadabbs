import tornado.ioloop
import tornado.web
import tornado.util
from db import *
import os
import json
import math
from datetime import datetime


# 复杂对象转json


class JsonEncoderCls(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, Topic):
            return o.__dict__
        else:
            if o.__class__.__name__ == "InstanceState":
                return  ''
            return json.JSONEncoder.default(self, o)


# 最新消息
news = []
page_size = 10

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = db_session()

    def on_finish(self):
        self.session.close()

    def get_current_user(self):
        return self.get_secure_cookie("user")

    @property
    def current_user(self):
        return int(self.get_current_user()) if self.get_current_user() else 0
    @property
    def is_auth(self):
        return True if self.get_current_user() else False


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")
        # self.write('<html><body><form action="/login" method="post">'
        #            'Name:<input type="text" name="name"><br/>'
        #            'Password:<input type="password" name="password"><br/>'
        #            '<input type="submit" value="Sign in">'
        #            '</form></body></html>')

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
        cur_page = int(self.get_argument("page", 0))
        topics = self.session.query(Topic).order_by(-Topic.id)
        count = topics.count()
        page_count = math.ceil(count/page_size)
        page_obj = topics.offset(cur_page*page_size).limit(page_size).all()
        data = {"topics": page_obj, "page": cur_page, "count": range(page_count)}
        self.render("index.html", data=data)


class DetailHandler(BaseHandler):
    def get(self, id):
        topic = self.session.query(Topic).filter(Topic.id==id).one()
        self.render("detail.html", topic=topic)


class PostTopicHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("post.html")

    @tornado.web.authenticated
    def post(self):
        title = self.get_argument("title")
        content = self.get_argument("content")
        uid = int(self.get_current_user())
        topic = Topic(title=title, content=content, user_id=uid)
        self.session.add(topic)
        self.session.commit()
        self.redirect("/")


class ReplyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(self.get_current_user())
        tid = self.get_argument("id")
        data = self.get_argument("data")
        try:
            comment = Comment(user_id=uid, content=data, topic_id=tid)
            self.session.add(comment)
            self.session.commit()
            self.write(json.dumps({"state": 1}))
        except:
            self.write(json.dumps({"state": 0}))


class NewTopicsHandler(BaseHandler):
    def get(self):
        news_json = json.dumps({"news": news, "state": 1}, cls=JsonEncoderCls)
        self.write(news_json)


settings = dict(
            blog_title=u"Tornado BBS",
            template_path=os.path.join(os.path.dirname(__file__), "tpl"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
            autoreload=False,
            login_url="/login"
        )


def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/detail/(\d+)", DetailHandler),
        (r"/post", PostTopicHandler),
        (r"/reply", ReplyHandler),
        (r"/login", LoginHandler),
        (r"/newTopic", NewTopicsHandler)
    ], **settings)


def time_call():
    global news
    session = db_session()
    news = session.query(Topic).order_by(-Topic.id).limit(5).all()


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    time_call()
    tornado.ioloop.PeriodicCallback(time_call, 36000000).start()
    tornado.ioloop.IOLoop.current().start()