import random
from conf import DAYS_BACK, DAYS_FORWARD, NUMBER_OF_WORK_ORDERS
from erp_tables import BillOfMaterials, Product, WorkOrder
from datetime import datetime, timedelta


def generate_work_orders(session):
    for _ in range(NUMBER_OF_WORK_ORDERS):
        id = random.randint(500000, 599999)

        product_ids = [
            row[0] for row in session.query(BillOfMaterials.product_id).distinct().all()
        ]
        product_id = random.choice(product_ids)
        uom = session.query(Product.uom).filter(Product.id == product_id).first()[0]

        today = datetime.now()
        back_date = today - timedelta(days=DAYS_BACK)
        start_date = back_date + timedelta(
            days=random.randint(0, (DAYS_BACK + DAYS_FORWARD))
        )
        quantity = random.randint(50, 250) * 10
        session.add(
            WorkOrder(
                id=id,
                product_id=product_id,
                start_date=start_date,
                quantity=quantity,
                uom=uom,
            )
        )
    return


def process_work_orders(session):
    for work_order in session.query(WorkOrder).all():
        print(work_order.id)
