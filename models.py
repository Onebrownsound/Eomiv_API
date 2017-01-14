from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    time_stamp = Column(String(120))
    ip = Column(String(20))
    country = Column(String(20))

    def __init__(self, id=None, ip=None, country=None, timestamp=None):
        self.id = id
        self.ip = ip
        self.country = country
        self.time_stamp = timestamp

    def __repr__(self):
        return '<User %r>' % (self.id)


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    action_type = Column(String(10))
    owner = Column(Integer)
    video_id = Column(Integer)

    def __init__(self, id=None, action_type=None, owner=None, video_id=None, timestamp=None):
        self.id = id
        self.action_type = action_type
        self.owner = owner
        self.video_id = video_id
        self.timestamp = timestamp

    def __repr__(self):
        return 'This is a {} owned by {} for video {}'.format(self.action_type, self.owner, self.video_id)
