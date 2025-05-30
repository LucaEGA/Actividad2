from flask import Blueprint, request, jsonify
from ..models import Product, db
from ..utils.decorators import token_required

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json()
    required_fields = ['product_code', 'product_name', 'cost']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Missing required fields: {required_fields}'}), 400

    if Product.query.filter_by(product_code=data['product_code']).first():
        return jsonify({'message': 'Product code already exists'}), 400

    new_product = Product(
        product_code=data['product_code'],
        product_name=data['product_name'],
        sku=data.get('sku'),
        unit_of_measure=data.get('unit_of_measure'),
        cost=data['cost'],
        sale_price=data.get('sale_price'),
        category=data.get('category'),
        location=data.get('location'),
        active=data.get('active', True)
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
        'id': new_product.id, 'product_code': new_product.product_code,
        'product_name': new_product.product_name, 'cost': new_product.cost
    }), 201

@product_bp.route('', methods=['GET'])
@token_required
def get_products(current_user):
    products = Product.query.all()
    return jsonify([{
        'id': p.id, 'product_code': p.product_code, 'product_name': p.product_name,
        'sku': p.sku, 'unit_of_measure': p.unit_of_measure, 'cost': p.cost,
        'sale_price': p.sale_price, 'category': p.category, 'location': p.location,
        'active': p.active, 'created_at': p.created_at, 'updated_at': p.updated_at
    } for p in products])

@product_bp.route('/<int:product_id>', methods=['GET'])
@token_required
def get_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id, 'product_code': product.product_code, 'product_name': product.product_name,
        'sku': product.sku, 'unit_of_measure': product.unit_of_measure, 'cost': product.cost,
        'sale_price': product.sale_price, 'category': product.category, 'location': product.location,
        'active': product.active, 'created_at': product.created_at, 'updated_at': product.updated_at
    })

@product_bp.route('/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    if 'product_code' in data and data['product_code'] != product.product_code:
        if Product.query.filter_by(product_code=data['product_code']).first():
            return jsonify({'message': 'Product code already exists'}), 400
        product.product_code = data['product_code']

    product.product_name = data.get('product_name', product.product_name)
    product.sku = data.get('sku', product.sku)
    product.unit_of_measure = data.get('unit_of_measure', product.unit_of_measure)
    product.cost = data.get('cost', product.cost)
    product.sale_price = data.get('sale_price', product.sale_price)
    product.category = data.get('category', product.category)
    product.location = data.get('location', product.location)
    product.active = data.get('active', product.active)

    db.session.commit()
    return jsonify({'id': product.id, 'product_name': product.product_name, 'message': 'Product updated'})

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    # Consider handling related movements or stock if any strict FK constraints exist
    # For PoC, simple delete.
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})
