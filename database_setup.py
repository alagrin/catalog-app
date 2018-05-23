import os
import sys
import sqlite3 # needed??
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

class Item(Base):
    __tablename__ = 'items'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category = Column(String(250))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    room = relationship(Room)

@property
def serialize(self):
    """Return object data in easily serializable format"""
    return {
        'name': self.name,
        'description': self.description,
        'category': self.category
    }

engine = create_engine('sqlite:///useritemcatalog.db')
Base.metadata.create_all(engine)