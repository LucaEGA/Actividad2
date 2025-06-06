from app import create_app, db
from app.models import User, Product, InventoryMovement, PredictorStockData # Import all models

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates tables if they don't exist
    app.run(debug=True)
