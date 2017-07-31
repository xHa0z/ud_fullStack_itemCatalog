from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Department, Base, Stock, User

engine = create_engine('postgresql://catalog:dummy@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
user_admin = User(name='admin', email='admin@mail.com');
session.add(user_admin)
session.commit()

# Stock for Auto
dept1 = Department(name="Auto", user_id=1)

session.add(dept1)
session.commit()

stock1 = Stock(name="Air Filter", brand="ACF",
                  num_in_stock=60, department=dept1, user_id=1)

session.add(stock1)
session.commit()


stock2 = Stock(name="Wiper Fluid", brand="OXG",
               num_in_stock=35, department=dept1, user_id=1)

session.add(stock2)
session.commit()

stock3 = Stock(name="Spark Plug", brand="CSD",
               num_in_stock=120, department=dept1, user_id=1)

session.add(stock3)
session.commit()

stock4 = Stock(name="All Season Mat", brand="MTT",
               num_in_stock=77, department=dept1, user_id=1)

session.add(stock4)
session.commit()



# Stock for Electronics
dept2 = Department(name="Electronics", user_id=1)

session.add(dept2)
session.commit()

stock1 = Stock(name="CPU", brand="ITL",
                  num_in_stock=60, department=dept2, user_id=1)

session.add(stock1)
session.commit()


stock2 = Stock(name="DLSR", brand="CNS",
               num_in_stock=12, department=dept2, user_id=1)

session.add(stock2)
session.commit()

stock3 = Stock(name="Projector", brand="ESP",
               num_in_stock=34, department=dept2, user_id=1)

session.add(stock3)
session.commit()

stock4 = Stock(name="Wireless Headset", brand="SNY",
               num_in_stock=67, department=dept2, user_id=1)

session.add(stock4)
session.commit()

stock5 = Stock(name="Tablet", brand="GLP",
               num_in_stock=23, department=dept2, user_id=1)

session.add(stock4)
session.commit()


# Stock for Outdoors
dept3 = Department(name="Outdoors", user_id=1)

session.add(dept3)
session.commit()

stock1 = Stock(name="Tent", brand="STK",
                  num_in_stock=23, department=dept3, user_id=1)

session.add(stock1)
session.commit()


stock2 = Stock(name="Bike", brand="SSZ",
               num_in_stock=7, department=dept3, user_id=1)

session.add(stock2)
session.commit()

stock3 = Stock(name="Backpack", brand="NFT",
               num_in_stock=38, department=dept3, user_id=1)

session.add(stock3)
session.commit()

print "stock added"
