from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    product_name = db.Column(db.String(128), nullable=False)
    sku = db.Column(db.String(64))
    unit_of_measure = db.Column(db.String(32))
    cost = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float)
    category = db.Column(db.String(64))
    location = db.Column(db.String(64))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    inventory_movements = db.relationship('InventoryMovement', backref='product', lazy='dynamic')
    predictor_data = db.relationship('PredictorStockData', backref='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.product_name}>'

class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    movement_type = db.Column(db.String(32), nullable=False)  # 'INBOUND', 'OUTBOUND', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT'
    quantity = db.Column(db.Integer, nullable=False) # Always positive
    movement_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    order_id = db.Column(db.String(64))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<InventoryMovement {self.id} for product {self.product_id}>'

class PredictorStockData(db.Model):
    __tablename__ = 'predictor_stock_data'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    avg_sale_price = db.Column(db.Float)
    promotion_active = db.Column(db.Boolean, default=False)
    special_event = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<PredictorStockData {self.id} for product {self.product_id} on {self.date}>'
