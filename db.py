from sqlalchemy import Column, String, Text, create_engine, Integer, Sequence, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {"mysql_engine": 'InnoDB'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_date = Column(DateTime, default=datetime.now)
    update_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)



Base = declarative_base(cls=BaseModel)
engine = create_engine("sqlite:///bbs.db", echo=True)
db_session = sessionmaker(bind=engine)


class User(Base):
    name = Column(String(16))
    phone = Column(String(16))
    password = Column(String(16))

    topics = relationship("Topic")
    comments = relationship("Comment")


class Topic(Base):
    title = Column(String(256))
    content = Column(Text)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="topics")
    comments = relationship("Comment")


class Comment(Base):
    content = Column(Text)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="comments")
    topic_id = Column(Integer, ForeignKey('topic.id'))
    topic = relationship("Topic", back_populates="comments")


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)

