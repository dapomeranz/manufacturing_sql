# models.py
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base

ErpBase = declarative_base()


class WorkOrder(ErpBase):
    __tablename__ = "erp_work_orders"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    start_date = Column(Date)
    complete_date = Column(Date)
    quantity = Column(Float)
    uom = Column(String)


class Product(ErpBase):
    __tablename__ = "erp_products"

    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    uom = Column(String)


class BillOfMaterials(ErpBase):
    __tablename__ = "erp_bill_of_materials"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    material_id = Column(Integer)
    operation_sequence = Column(Integer)
    quantity = Column(Float)
    uom = Column(String)


class Route(ErpBase):
    __tablename__ = "erp_routes"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    operation_name = Column(Integer)
    sequence = Column(Integer)


class InventorySummary(ErpBase):
    __tablename__ = "erp_inventory_summary"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    quantity = Column(Float)
    uom = Column(String)
