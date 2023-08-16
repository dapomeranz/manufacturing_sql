from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from erp_tables import ErpBase, generate_work_orders
from mes_tables import MesBase

import os
import pandas as pd
import random


def load_master_data_tables(engine):
    ## take the data from the csvs in /master_data and load them into the database
    for file in os.listdir("master_data"):
        df = pd.read_csv(os.path.join("master_data", file))
        ## if the dataframe does not contain a column called id, add one with a random 5 digit integer
        if "id" not in df.columns:
            random_ids = [random.randint(10000, 99999) for _ in range(len(df))]
            df.insert(0, "id", random_ids)
        ## add the data to the database into a table which is the same as the file name
        df.to_sql(file.split(".")[0], con=engine, if_exists="append", index=False)


DATABASE_URL = "sqlite:///mfg_database.sqlite3"
engine = create_engine(DATABASE_URL, echo=True)

MesBase.metadata.drop_all(engine)
ErpBase.metadata.drop_all(engine)
MesBase.metadata.create_all(engine)
ErpBase.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

load_master_data_tables(engine)
generate_work_orders(session)
session.commit()
session.close()
