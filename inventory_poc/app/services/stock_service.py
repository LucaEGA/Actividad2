from ..models import db, Product, InventoryMovement
from sqlalchemy.sql import func
from datetime import datetime, timezone

def get_current_stock_for_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return None

    inbound_qty = db.session.query(func.sum(InventoryMovement.quantity)).filter(
        InventoryMovement.product_id == product_id,
        InventoryMovement.movement_type.in_(['INBOUND', 'ADJUSTMENT_IN'])
    ).scalar() or 0

    outbound_qty = db.session.query(func.sum(InventoryMovement.quantity)).filter(
        InventoryMovement.product_id == product_id,
        InventoryMovement.movement_type.in_(['OUTBOUND', 'ADJUSTMENT_OUT'])
    ).scalar() or 0

    current_quantity = inbound_qty - outbound_qty

    last_movement = InventoryMovement.query.filter_by(product_id=product_id)                                           .order_by(InventoryMovement.movement_date.desc())                                           .first()

    last_updated = last_movement.movement_date if last_movement else product.created_at

    return {
        'product_id': product.id,
        'product_code': product.product_code,
        'product_name': product.product_name,
        'quantity': current_quantity,
        'last_updated': last_updated.isoformat() if last_updated else None,
        'total_inventory_cost': current_quantity * product.cost
    }

def get_all_current_stock():
    products = Product.query.all()
    stock_list = []
    for p in products:
        stock_data = get_current_stock_for_product(p.id)
        if stock_data:
            stock_list.append(stock_data)
    return stock_list
