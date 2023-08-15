# models.py
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

MesBase = declarative_base()


class Operation(MesBase):
    __tablename__ = "mes_operations"

    id = Column(Integer, primary_key=True)
    operation_name = Column(String)


class Resource(MesBase):
    __tablename__ = "mes_resources"

    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer)
    resource_name = Column(String)


class Operator(MesBase):
    __tablename__ = "mes_operators"

    id = Column(Integer, primary_key=True)
    operator_name = Column(String)


class CompleteLog(MesBase):
    __tablename__ = "mes_complete_logs"

    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer)
    resource_id = Column(Integer)
    operator_id = Column(Integer)
    work_order_id = Column(Integer)
    timestamp = Column(DateTime)
    quantity = Column(Float)


class ScrapLog(MesBase):
    __tablename__ = "mes_scrap_logs"

    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer)
    resource_id = Column(Integer)
    operator_id = Column(Integer)
    work_order_id = Column(Integer)
    timestamp = Column(DateTime)
    quantity = Column(Float)


class DataCaptureLog(MesBase):
    __tablename__ = "mes_data_capture_logs"

    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer)
    resource_id = Column(Integer)
    operator_id = Column(Integer)
    work_order_id = Column(Integer)
    timestamp = Column(DateTime)
    data_point_name = Column(String)
    value = Column(Float)
    uom = Column(String)
