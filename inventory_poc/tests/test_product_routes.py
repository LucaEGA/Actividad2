import json
from app.models import Product

def test_create_product_success(auth_client, init_database):
    response = auth_client.post('/api/v1/products', json={
        'product_code': 'P001_TEST',
        'product_name': 'Test Product 1',
        'cost': 10.99,
        'sale_price': 15.99
    }, headers=auth_client.auth_headers)
    assert response.status_code == 201
    assert response.json['product_code'] == 'P001_TEST'
    assert Product.query.filter_by(product_code='P001_TEST').first() is not None

def test_create_product_missing_fields(auth_client, init_database):
    response = auth_client.post('/api/v1/products', json={
        'product_name': 'Test Product Incomplete'
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Missing required fields' in response.json['message']

def test_create_product_duplicate_code(auth_client, init_database):
    auth_client.post('/api/v1/products', json={
        'product_code': 'P002_DUP', 'product_name': 'First Prod', 'cost': 5.00
    }, headers=auth_client.auth_headers)
    response = auth_client.post('/api/v1/products', json={
        'product_code': 'P002_DUP', 'product_name': 'Second Prod', 'cost': 6.00
    }, headers=auth_client.auth_headers)
    assert response.status_code == 400
    assert 'Product code already exists' in response.json['message']

def test_get_products_list(auth_client, init_database):
    auth_client.post('/api/v1/products', json={
        'product_code': 'P003_LIST1', 'product_name': 'Prod List 1', 'cost': 1.00
    }, headers=auth_client.auth_headers)
    auth_client.post('/api/v1/products', json={
        'product_code': 'P004_LIST2', 'product_name': 'Prod List 2', 'cost': 2.00
    }, headers=auth_client.auth_headers)

    response = auth_client.get('/api/v1/products', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 2 # Could be more if other tests added products

def test_get_single_product(auth_client, init_database):
    create_resp = auth_client.post('/api/v1/products', json={
        'product_code': 'P005_SINGLE', 'product_name': 'Single Prod', 'cost': 3.00
    }, headers=auth_client.auth_headers)
    product_id = create_resp.json['id']

    response = auth_client.get(f'/api/v1/products/{product_id}', headers=auth_client.auth_headers)
    assert response.status_code == 200
    assert response.json['product_code'] == 'P005_SINGLE'

def test_get_single_product_not_found(auth_client, init_database):
    response = auth_client.get('/api/v1/products/9999', headers=auth_client.auth_headers) # Non-existent ID
    assert response.status_code == 404
