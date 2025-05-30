import os
from dotenv import load_dotenv
load_dotenv() # Load .env variables first

from app import create_app, db
from app.models import User, Product, InventoryMovement, PredictorStockData

# Determine the project root and database file name from .env or use a default
project_root = os.path.dirname(os.path.abspath(__file__))
db_file_name = os.getenv('DATABASE_URL', 'sqlite:///inventory_poc.db').replace('sqlite:///', '')
actual_db_path = os.path.join(project_root, db_file_name)

def initialize_database():
    app = create_app()
    with app.app_context():
        # If the database file exists, delete it to start fresh
        if os.path.exists(actual_db_path):
            print(f"Deleting existing database: {actual_db_path}")
            os.remove(actual_db_path)

        print("Creating all database tables...")
        db.create_all()
        print("Database tables created.")

        # Optional: Add some seed data
        if not User.query.first():
            print("Adding seed admin user...")
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user 'admin' with password 'admin123' created.")

        print("Database initialized successfully.")

if __name__ == '__main__':
    print(f"This script will initialize the database at: {actual_db_path}")
    confirmation = input("Are you sure you want to proceed? This will delete existing data if the DB file exists. (yes/no): ")
    if confirmation.lower() == 'yes':
        initialize_database()
    else:
        print("Database initialization cancelled.")
