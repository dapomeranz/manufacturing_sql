from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from erp_tables import ErpBase

from mes_tables import MesBase

DATABASE_URL = "sqlite:///mfg_database.db"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()
MesBase.metadata.create_all(engine)
ErpBase.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
session.commit()
session.close()
