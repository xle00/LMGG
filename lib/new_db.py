from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, Boolean, DateTime, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os

Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(12), unique=True, nullable=False)
    is_admin = Column('is_admin', Boolean, default=False)
    admin = Column("admin", String(12))
    first_seen = Column('first_seen', DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.name


class Gifts(Base):
    __tablename__ = 'gifts'
    id = Column('id', Integer, primary_key=True)
    gift_timestamp = Column('gift_timestamp', DateTime, nullable=False)
    gift = Column('gift', String(80), nullable=False)
    member = Column('member', String(12), nullable=False)
    level = Column('level', Integer, nullable=False)
    _type = Column('type', Integer, nullable=False)
    added_timestamp = Column('added_timestamp', DateTime, default=datetime.utcnow)
    reset_time = Column('reset_time', Integer)

    def __repr__(self):
        return f'Lv. {self.level} {self.gift} | {self.member} | {self.gift_timestamp}'


db_path = os.path.join(os.getenv('APPDATA'), "lmgg_data.db")
print(db_path)
db = create_engine(f"sqlite:///{db_path}", echo=False)
Base.metadata.create_all(bind=db)
Session = sessionmaker(bind=db)
session = Session()


def add_member(name):
    member = Member()
    member.name = name
    try:
        session.add(member)
        session.commit()
    except IntegrityError:
        session.rollback()


def add_gift(gift_data):
    gift = Gifts()
    gift.gift_timestamp = gift_data[0]
    gift.level = gift_data[1]
    gift.gift = gift_data[2]
    gift.member = gift_data[3]
    gift._type = gift_data[4]
    gift.reset_time = gift_data[5]
    session.add(gift)
    session.commit()


def add_data(data):
    for d in data:
        add_member(d[-3])
        add_gift(d)


def get_all_members():
    return session.query(Member).all()


def get_member_dates(name):
    return session.execute(select(Gifts.gift_timestamp).where(Gifts.member == name)).all()


def get_gifts(name):
    return session.query(Gifts).filter_by(member=name).all()
