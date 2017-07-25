import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)


class Department(Base):
  __tablename__ = 'department'

  id = Column(Integer, primary_key=True)
  name = Column(String(127), nullable=False)
  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
    }


class Stock(Base):
  __tablename__ = "stock"

  id = Column(Integer, primary_key=True)
  name = Column(String(64), nullable=False)
  brand = Column(String(64))
  num_in_stock = Column(Integer)
  department_id = Column(Integer, ForeignKey('department.id'))
  department = relationship(Department)
  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User)



  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'brand': self.brand,
      'number': self.num_in_stock,
    }



engine = create_engine('sqlite:///stock_inventory.db')

Base.metadata.create_all(engine)