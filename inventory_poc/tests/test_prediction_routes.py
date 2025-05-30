import json
from app.models import Product, PredictorStockData, db
from datetime import date, timedelta

def test_add_predictor_data_success(auth_client, init_database):
    # Create a product
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_PRED01', 'product_name': 'Prediction Test Prod', 'cost': 30.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']

    today_str = date.today().isoformat()
    response = auth_client.post('/api/v1/stock/predictor-data', json={
        'product_id': product_id,
        'date': today_str,
        'units_sold': 10
    }, headers=auth_client.auth_headers)

    assert response.status_code == 201
    assert response.json['product_id'] == product_id
    assert response.json['units_sold'] == 10
    assert PredictorStockData.query.filter_by(product_id=product_id).count() == 1

def test_add_predictor_data_product_not_found(auth_client, init_database):
    response = auth_client.post('/api/v1/stock/predictor-data', json={
        'product_id': 998, # Non-existent
        'date': date.today().isoformat(),
        'units_sold': 5
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404 # Product not found from service
    assert 'Product not found' in response.json['message']

def test_get_predictor_data_for_product(auth_client, init_database):
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_PRED02', 'product_name': 'Pred Data Prod 2', 'cost': 25.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']

    # Add some data points
    for i in range(3):
        auth_client.post('/api/v1/stock/predictor-data', json={
            'product_id': product_id,
            'date': (date.today() - timedelta(days=i)).isoformat(),
            'units_sold': 10 + i
        }, headers=auth_client.auth_headers)

    response = auth_client.get(f'/api/v1/stock/predictor-data?product_id={product_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 3

def test_get_stock_prediction_sma(auth_client, init_database, app):
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_PRED03', 'product_name': 'SMA Pred Prod', 'cost': 15.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']

    # Add historical data (at least 'window_size' points)
    sales = [5, 7, 6, 8, 7] # 5 data points
    with app.app_context(): # Need app context to interact with db directly for setup
        for i, sale_units in enumerate(sales):
            entry = PredictorStockData(
                product_id=product_id,
                date=date.today() - timedelta(days=(len(sales) - 1 - i)), # Ensure chronological order
                units_sold=sale_units
            )
            db.session.add(entry)
        db.session.commit()

    # Test prediction with window=3, periods=2
    response = auth_client.get(f'/api/v1/stock/predict/{product_id}?periods=2&window=3', headers=auth_client.auth_headers)
    assert response.status_code == 200
    prediction_data = response.json
    assert prediction_data['product_id'] == product_id
    assert len(prediction_data['predictions']) == 2

    # SMA of last 3: (6+8+7)/3 = 21/3 = 7
    # PoC SMA predicts this same value for all future periods
    assert prediction_data['predictions'][0]['predicted_units_sold'] == 7
    assert prediction_data['predictions'][1]['predicted_units_sold'] == 7

def test_get_stock_prediction_not_enough_data(auth_client, init_database):
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_PRED04', 'product_name': 'Pred Insufficient Data', 'cost': 10.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']

    # Add only 1 data point
    auth_client.post('/api/v1/stock/predictor-data', json={
        'product_id': product_id,
        'date': date.today().isoformat(),
        'units_sold': 10
    }, headers=auth_client.auth_headers)

    response = auth_client.get(f'/api/v1/stock/predict/{product_id}?periods=1&window=3', headers=auth_client.auth_headers)
    assert response.status_code == 400 # Bad request due to insufficient data for SMA
    assert 'Not enough historical data' in response.json['message']

def test_get_stock_prediction_product_not_found(auth_client, init_database):
    response = auth_client.get('/api/v1/stock/predict/99999?periods=1&window=3', headers=auth_client.auth_headers)
    assert response.status_code == 404 # Product not found
    assert 'Product not found' in response.json['message']
