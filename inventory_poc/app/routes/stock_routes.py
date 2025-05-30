from flask import Blueprint, jsonify
from ..utils.decorators import token_required
from ..services.stock_service import get_current_stock_for_product, get_all_current_stock

stock_bp = Blueprint('stock_bp', __name__) # Will be registered with /api/v1/stock

@stock_bp.route('/current/<int:product_id>', methods=['GET'])
@token_required
def get_stock_single_product(current_user, product_id):
    stock_data = get_current_stock_for_product(product_id)
    if not stock_data:
        return jsonify({'message': 'Product not found or no stock information'}), 404
    return jsonify(stock_data)

@stock_bp.route('/current', methods=['GET'])
@token_required
def get_stock_all_products(current_user):
    all_stock_data = get_all_current_stock()
    return jsonify(all_stock_data)
