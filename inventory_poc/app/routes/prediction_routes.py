from flask import Blueprint, request, jsonify
from ..models import PredictorStockData, Product, db
from ..utils.decorators import token_required
from ..services.prediction_service import add_predictor_data_entry, get_predictor_data_for_product, predict_stock_simple_moving_average
from datetime import datetime

prediction_bp = Blueprint('prediction_bp', __name__) # Registered under /api/v1/stock

@prediction_bp.route('/predictor-data', methods=['POST'])
@token_required
def add_historical_data(current_user):
    data = request.get_json()
    required_fields = ['product_id', 'date', 'units_sold']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Missing required fields: {required_fields}'}), 400

    try:
        # Validate date format if necessary, though SQLAlchemy might handle some of it
        datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Date must be in YYYY-MM-DD format'}), 400

    entry, error = add_predictor_data_entry(data)
    if error:
        return jsonify({'message': error}), 404 # Product not found

    return jsonify({
        'id': entry.id, 'product_id': entry.product_id, 'date': entry.date.isoformat(),
        'units_sold': entry.units_sold, 'message': 'Predictor data entry added'
    }), 201

@prediction_bp.route('/predictor-data', methods=['GET'])
@token_required
def get_historical_data(current_user):
    product_id_filter = request.args.get('product_id', type=int)
    if not product_id_filter:
        return jsonify({'message': 'product_id query parameter is required'}), 400

    data_entries = get_predictor_data_for_product(product_id_filter)
    return jsonify([{
        'id': entry.id, 'product_id': entry.product_id, 'date': entry.date.isoformat(),
        'units_sold': entry.units_sold, 'avg_sale_price': entry.avg_sale_price,
        'promotion_active': entry.promotion_active, 'special_event': entry.special_event
    } for entry in data_entries])

@prediction_bp.route('/predict/<int:product_id>', methods=['GET'])
@token_required
def get_stock_prediction(current_user, product_id):
    periods = request.args.get('periods', default=3, type=int)
    window = request.args.get('window', default=3, type=int)

    if periods <=0 or window <=0:
        return jsonify({'message': 'Periods and window must be positive integers'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    predictions, error = predict_stock_simple_moving_average(product_id, periods_to_predict=periods, window_size=window)

    if error:
        return jsonify({'message': error}), 400

    return jsonify({
        'product_id': product_id,
        'product_code': product.product_code,
        'product_name': product.product_name,
        'periods_predicted': periods,
        'window_size_used': window,
        'predictions': predictions
    })
