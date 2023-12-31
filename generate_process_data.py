import random
from conf import (
    DAYS_BACK,
    DAYS_FORWARD,
    INVENTORY_START_QUANTITY,
    NUMBER_OF_WORK_ORDERS,
    SCRAP_RATE,
)
from erp_tables import BillOfMaterials, InventorySummary, Product, Route, WorkOrder
from datetime import datetime, timedelta

from mes_tables import CompleteLog, Operation, Operator, Resource, ScrapLog


def generate_work_orders(session):
    for _ in range(NUMBER_OF_WORK_ORDERS):
        id = random.randint(5000000, 5999999)

        product_ids = [
            row.product_id for row in session.query(BillOfMaterials).distinct().all()
        ]
        product_id = random.choice(product_ids)
        uom = session.query(Product).filter(Product.id == product_id).first().uom

        today = datetime.today()
        back_date = today - timedelta(days=DAYS_BACK)
        planned_start_date = back_date + timedelta(
            days=random.randint(0, (DAYS_BACK + DAYS_FORWARD))
        )
        time_difference = timedelta(
            days=random.randint(-2, 2),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        actual_start_timestamp = (
            datetime.combine(planned_start_date, datetime.min.time()) + time_difference
        )
        if actual_start_timestamp >= today:
            actual_start_timestamp = None
        quantity = random.randint(50, 250) * 10
        session.add(
            WorkOrder(
                id=id,
                product_id=product_id,
                planned_start_date=planned_start_date,
                actual_start_timestamp=actual_start_timestamp,
                original_quantity=quantity,
                uom=uom,
            )
        )


def generate_inventory(session):
    for bom_row in session.query(BillOfMaterials.material_id).distinct().all():
        material_id = bom_row.material_id
        uom = session.query(Product).filter(Product.id == material_id).first().uom
        id = random.randint(100000, 999999)
        session.add(
            InventorySummary(
                id=id,
                product_id=material_id,
                quantity=INVENTORY_START_QUANTITY
                if uom != "grams"
                else INVENTORY_START_QUANTITY * 10,
                uom=uom,
            )
        )

    for bom_row in session.query(BillOfMaterials.product_id).distinct().all():
        product_id = bom_row.product_id
        uom = session.query(Product).filter(Product.id == product_id).first().uom
        id = random.randint(100000, 999999)
        session.add(
            InventorySummary(
                id=id,
                product_id=product_id,
                quantity=0,
                uom=uom,
            )
        )


def process_route_step(session, work_order, route_step, step_no, is_last_step):
    ## Get quantity from previous step or from work order quantity if first step
    quantity_in_progress = (
        session.query(CompleteLog)
        .filter(CompleteLog.work_order_id == work_order.id)
        .order_by(CompleteLog.timestamp.desc())
        .first()
    )
    if quantity_in_progress is None:
        quantity_in_progress = work_order.original_quantity
    else:
        quantity_in_progress = quantity_in_progress.quantity

    ## Lower Inventory levels of materials
    for material in session.query(BillOfMaterials).filter(
        BillOfMaterials.product_id == work_order.product_id
    ):
        inventory_summary = (
            session.query(InventorySummary)
            .filter(
                InventorySummary.product_id == material.material_id,
                route_step.sequence == material.operation_sequence,
            )
            .first()
        )

        if inventory_summary is not None:
            inventory_summary.quantity -= material.quantity * quantity_in_progress
            session.commit()

    ## Randomly select a resource and operator
    operation_id = (
        session.query(Operation)
        .filter(Operation.operation_name == route_step.operation_name)
        .first()
        .id
    )
    resource_options = [
        row.id
        for row in session.query(Resource).filter(Resource.operation_id == operation_id)
    ]
    resource = random.choice(resource_options)
    operator_options = [row.id for row in session.query(Operator)]
    operator = random.choice(operator_options)

    ## Randomly generate time of day
    day = work_order.actual_start_timestamp + timedelta(days=step_no)
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    random_timestamp = datetime.combine(day, datetime.min.time()) + random_time

    ## Randomly generate logs
    random_scrap_rate = random.randint(0, 4) * SCRAP_RATE
    if route_step.operation_name == "inspection":
        random_scrap_rate *= 2
    scrap_quantity = round(quantity_in_progress * random_scrap_rate, 2)
    session.add(
        CompleteLog(
            id=random.randint(10000000, 99999999),
            resource_id=resource,
            operator_id=operator,
            work_order_id=work_order.id,
            timestamp=random_timestamp,
            quantity=quantity_in_progress - scrap_quantity,
        )
    )
    if scrap_quantity > 0:
        session.add(
            ScrapLog(
                id=random.randint(10000000, 99999999),
                resource_id=resource,
                operator_id=operator,
                work_order_id=work_order.id,
                timestamp=random_timestamp,
                quantity=scrap_quantity,
            )
        )

    ## If final completion, update work order and inventory or create record
    if is_last_step:
        work_order.complete_timestamp = random_timestamp
        work_order.completed_quantity = quantity_in_progress - scrap_quantity
        inv = (
            session.query(InventorySummary)
            .filter(InventorySummary.product_id == work_order.product_id)
            .first()
        )
        if inv is None:
            uom = (
                session.query(Product)
                .filter(Product.id == work_order.product_id)
                .first()
                .uom
            )
            id = random.randint(100000, 999999)
            session.add(
                InventorySummary(
                    id=id,
                    product_id=work_order.product_id,
                    quantity=quantity_in_progress - scrap_quantity,
                    uom=uom,
                )
            )
        inv.quantity += quantity_in_progress - scrap_quantity


def process_work_orders(session):
    for work_order in session.query(WorkOrder).all():
        if work_order.actual_start_timestamp is None:
            continue
        ordered_route_steps = (
            session.query(Route)
            .filter(Route.product_id == work_order.product_id)
            .order_by(Route.sequence)
            .all()
        )
        for i, route_step in enumerate(ordered_route_steps):
            if work_order.actual_start_timestamp + timedelta(days=i) > datetime.today():
                break
            is_last_step = i + 1 == len(ordered_route_steps)
            process_route_step(
                session,
                work_order,
                route_step,
                i + 1,
                is_last_step,
            )
