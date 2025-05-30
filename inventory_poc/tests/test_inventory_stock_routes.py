import json
from app.models import Product, InventoryMovement, db
from app.services.stock_service import get_current_stock_for_product

def test_record_inventory_movement_success(auth_client, init_database):
    # Create a product first
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_INV001', 'product_name': 'Inventory Test Prod', 'cost': 20.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']

    response = auth_client.post('/api/v1/inventory/movements', json={
        'product_id': product_id,
        'movement_type': 'INBOUND',
        'quantity': 100,
        'order_id': 'PO123'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    assert response.json['movement_type'] == 'INBOUND'
    assert response.json['quantity'] == 100
    assert InventoryMovement.query.filter_by(product_id=product_id).count() == 1

def test_record_movement_product_not_found(auth_client, init_database):
    response = auth_client.post('/api/v1/inventory/movements', json={
        'product_id': 999, # Non-existent product
        'movement_type': 'INBOUND',
        'quantity': 10
    }, headers=auth_client.auth_headers)
    assert response.status_code == 404 # Product not found
    assert 'Product not found' in response.json['message']

def test_record_movement_invalid_type(auth_client, init_database):
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_INV002', 'product_name': 'Inv Test Prod 2', 'cost': 20.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']
    response = auth_client.post('/api/v1/inventory/movements', json={
        'product_id': product_id,
        'movement_type': 'INVALID_TYPE',
        'quantity': 10
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Invalid movement type' in response.json['message']


def test_get_current_stock_calculation(auth_client, init_database, app): # Added app fixture
    # Create product
    product_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P_STOCK01', 'product_name': 'Stock Calc Prod', 'cost': 10.00
    }, headers=auth_client.auth_headers)
    product_id = product_resp.json['id']

    # Record movements
    auth_client.post('/api/v1/inventory/movements', json={
        'product_id': product_id, 'movement_type': 'INBOUND', 'quantity': 50
    }, headers=auth_client.auth_headers)
    auth_client.post('/api/v1/inventory/movements', json={
        'product_id': product_id, 'movement_type': 'OUTBOUND', 'quantity': 10
    }, headers=auth_client.auth_headers)
    auth_client.post('/api/v1/inventory/movements', json={
        'product_id': product_id, 'movement_type': 'ADJUSTMENT_IN', 'quantity': 5
    }, headers=auth_client.auth_headers)
    auth_client.post('/api/v1/inventory/movements', json={
        'product_id': product_id, 'movement_type': 'ADJUSTMENT_OUT', 'quantity': 2
    }, headers=auth_client.auth_headers)

    # Test API endpoint for current stock
    response_api = auth_client.get(f'/api/v1/stock/current/{product_id}', headers=auth_client.auth_headers)
    assert response_api.status_code == 200
    stock_data_api = response_api.json
    # Expected: 50 - 10 + 5 - 2 = 43
    assert stock_data_api['quantity'] == 43
    assert stock_data_api['total_inventory_cost'] == 43 * 10.00

    # Test service function directly (requires app context)
    with app.app_context():
        stock_data_service = get_current_stock_for_product(product_id)
        assert stock_data_service is not None
        assert stock_data_service['quantity'] == 43
        assert stock_data_service['total_inventory_cost'] == 43 * 10.00

def test_get_all_current_stock(auth_client, init_database):
    # Add a couple of products and movements
    p1_resp = auth_client.post('/api/v1/products', json={'product_code': 'P_ALLS01', 'product_name':'AllStock1', 'cost':5}, headers=auth_client.auth_headers)
    p1_id = p1_resp.json['id']
    auth_client.post('/api/v1/inventory/movements', json={'product_id': p1_id, 'movement_type': 'INBOUND', 'quantity': 10}, headers=auth_client.auth_headers)

    p2_resp = auth_client.post('/api/v1/products', json={'product_code': 'P_ALLS02', 'product_name':'AllStock2', 'cost':8}, headers=auth_client.auth_headers)
    p2_id = p2_resp.json['id']
    auth_client.post('/api/v1/inventory/movements', json={'product_id': p2_id, 'movement_type': 'INBOUND', 'quantity': 20}, headers=auth_client.auth_headers)
    auth_client.post('/api/v1/inventory/movements', json={'product_id': p2_id, 'movement_type': 'OUTBOUND', 'quantity': 5}, headers=auth_client.auth_headers)

    response = auth_client.get('/api/v1/stock/current', headers=auth_client.auth_headers)
    assert response.status_code == 200
    all_stock = response.json
    assert isinstance(all_stock, list)
    # The number of items in all_stock can be >= 2 depending on other tests

    found_p1 = next((s for s in all_stock if s['product_id'] == p1_id), None)
    found_p2 = next((s for s in all_stock if s['product_id'] == p2_id), None)

    assert found_p1 is not None
    assert found_p1['quantity'] == 10

    assert found_p2 is not None
    assert found_p2['quantity'] == 15 # 20 - 5
