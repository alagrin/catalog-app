from sqlalchemy import Column, ForeignKey, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    password = Column(String(80), nullable=False, unique=True)


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, Sequence('item_seq'), primary_key=True)
    name = Column(String(80), nullable=False)

class Item(Base):
    __tablename__ = 'items'

    name = Column(String(80), nullable=False)
    id = Column(Integer, Sequence('item_seq', start=1), primary_key=True)
    description = Column(String(250))
    category = Column(String(250), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    room = relationship("Room", backref="items", cascade="all, delete")

@property
def serialize(self):
    """Return item data in easily serializable format"""
    return {
        'name': self.name,
        'description': self.description,
        'category': self.category
    }

engine = create_engine('sqlite:///useritemcatalog.db')
Base.metadata.create_all(engine)