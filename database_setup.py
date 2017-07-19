import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Department(Base):
  __tablename__ = 'department'

  id = Column(Integer, primary_key=True)
  name = Column(String(127), nullable=False)

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
  description = Column(String(250))
  num_in_stock = Column(Integer)
  department_id = Column(Integer, ForeignKey('department.id'))
  department = relationship(Department)



  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'number': self.num_in_stock,
    }



engine = create_engine('sqlite:///stock_inventory.db')

Base.metadata.create_all(engine)