from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app) # Basic CORS setup for all origins

    db.init_app(app)

    from .routes.auth_routes import auth_bp
    from .routes.product_routes import product_bp
    from .routes.inventory_routes import inventory_bp
    from .routes.stock_routes import stock_bp
    from .routes.prediction_routes import prediction_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(product_bp, url_prefix='/api/v1/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(stock_bp, url_prefix='/api/v1/stock')
    app.register_blueprint(prediction_bp, url_prefix='/api/v1/stock') # Prediction routes are also under /stock

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/') # Default to login page, or dashboard if logged in (client-side check)
    def index_page():
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard_page():
        # Client-side JS will check for token and redirect to login if necessary
        return render_template('dashboard.html')

    return app
