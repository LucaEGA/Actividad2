from flask import Blueprint, request, jsonify
from ..models import InventoryMovement, Product, db
from ..utils.decorators import token_required
from datetime import datetime, timezone

inventory_bp = Blueprint('inventory_bp', __name__)

@inventory_bp.route('/movements', methods=['POST'])
@token_required
def record_movement(current_user):
    data = request.get_json()
    required_fields = ['product_id', 'movement_type', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Missing required fields: {required_fields}'}), 400

    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    valid_movement_types = ['INBOUND', 'OUTBOUND', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT']
    if data['movement_type'] not in valid_movement_types:
        return jsonify({'message': f'Invalid movement type. Must be one of {valid_movement_types}'}), 400

    if not isinstance(data['quantity'], int) or data['quantity'] <= 0:
        return jsonify({'message': 'Quantity must be a positive integer'}), 400

    # For PoC, we'll update stock implicitly. A more robust system might have explicit stock updates.
    new_movement = InventoryMovement(
        product_id=data['product_id'],
        movement_type=data['movement_type'],
        quantity=data['quantity'], # Stored as positive, type dictates calculation
        movement_date=datetime.now(timezone.utc), # Or allow user to specify
        order_id=data.get('order_id'),
        notes=data.get('notes')
    )
    db.session.add(new_movement)
    db.session.commit()

    # from ..services.stock_service import get_current_stock_for_product # To return updated stock
    # updated_stock = get_current_stock_for_product(data['product_id'])

    return jsonify({
        'id': new_movement.id, 'product_id': new_movement.product_id,
        'movement_type': new_movement.movement_type, 'quantity': new_movement.quantity,
        'message': 'Movement recorded'
        # 'current_stock': updated_stock # Optionally return current stock
    }), 201

@inventory_bp.route('/movements', methods=['GET'])
@token_required
def get_movements(current_user):
    product_id_filter = request.args.get('product_id', type=int)
    query = InventoryMovement.query
    if product_id_filter:
        query = query.filter_by(product_id=product_id_filter)

    movements = query.order_by(InventoryMovement.movement_date.desc()).all()
    return jsonify([{
        'id': m.id, 'product_id': m.product_id, 'product_name': m.product.product_name,
        'movement_type': m.movement_type, 'quantity': m.quantity,
        'movement_date': m.movement_date.isoformat(), 'order_id': m.order_id, 'notes': m.notes
    } for m in movements])
