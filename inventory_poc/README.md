# Inventory Management and Stock Prediction PoC

This project is a Proof of Concept (PoC) for an inventory management system with a stock prediction module. It includes a backend API built with Flask and a basic HTML/JavaScript frontend for interaction.

## Features Implemented (PoC Scope)

*   **User Management:**
    *   User registration (username, password).
    *   User login with simple token-based authentication.
*   **Product Master Data:**
    *   Add new products (name, code, cost, etc.).
    *   View a list of products.
*   **Inventory Movement:**
    *   Record inbound, outbound, and adjustment movements for products.
    *   View recent movements.
*   **Current Stock Display:**
    *   View current stock quantity and total inventory cost for each product.
    *   Stock levels are dynamically calculated from movements.
*   **Basic Stock Prediction:**
    *   Add historical sales data for products.
    *   Get a simple moving average (SMA) prediction for future stock/sales for a selected product.
*   **Basic Frontend:**
    *   HTML pages for login, registration, and a dashboard to interact with the above features.
*   **Unit Tests:**
    *   Basic unit tests for backend API endpoints and services.

## Technology Stack

*   **Backend:** Python 3.x, Flask
*   **Database:** SQLite (for PoC)
*   **Authentication:** Simple JWT (PyJWT) for API protection.
*   **Frontend:** Basic HTML, CSS, JavaScript (no complex frameworks for PoC).
*   **Testing:** pytest
*   **Environment Management:** python-dotenv

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   A virtual environment tool (like `venv`)

## Setup Instructions

1.  **Clone the Repository (Example):**
    ```bash
    # git clone <repository_url> # If this were a git repo
    # cd inventory_poc
    ```
    For now, assume you have the `inventory_poc` directory.

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Copy the example environment file and customize if needed (especially `SECRET_KEY` for a real deployment, though the default works for local PoC).
    ```bash
    cp .env.example .env
    ```
    The default `.env` will use `sqlite:///inventory_poc.db`.

5.  **Initialize the Database:**
    This script creates the database schema (`inventory_poc.db` file in the project root) and adds a default admin user.
    ```bash
    python init_db.py
    ```
    The script will confirm before running. Default admin credentials:
    *   Username: `admin`
    *   Password: `admin123`

## Running the Application

1.  **Start the Flask Development Server:**
    ```bash
    python run.py
    ```
    The application will typically be available at `http://127.0.0.1:5000`.

2.  **Access the Frontend:**
    Open your web browser and navigate to:
    *   Login: `http://127.0.0.1:5000/login`
    *   Dashboard (after login): `http://127.0.0.1:5000/dashboard`

## Running Tests

Ensure your virtual environment is activated and dependencies (including `pytest`) are installed.

```bash
pytest
# or
python -m pytest
```
Tests use an in-memory SQLite database and do not affect `inventory_poc.db`.

## API Endpoints Overview

The backend API is available under the base URL: `/api/v1`. All non-auth routes require a Bearer token.

*   **Authentication:**
    *   `POST /auth/register`
    *   `POST /auth/login`
*   **Products:**
    *   `POST /products`
    *   `GET /products`
    *   `GET /products/<id>`
    *   `PUT /products/<id>`
    *   `DELETE /products/<id>`
*   **Inventory Movements:**
    *   `POST /inventory/movements`
    *   `GET /inventory/movements`
*   **Current Stock:**
    *   `GET /stock/current/<product_id>`
    *   `GET /stock/current`
*   **Stock Prediction:**
    *   `POST /stock/predictor-data` (to add historical sales)
    *   `GET /stock/predictor-data?product_id=<id>`
    *   `GET /stock/predict/<product_id>?periods=<N>&window=<M>`

## Project Directory Structure (Key Files/Dirs)

```
inventory_poc/
├── app/                    # Main Flask application package
│   ├── __init__.py         # Application factory
│   ├── config.py           # Configuration settings
│   ├── models.py           # SQLAlchemy database models
│   ├── routes/             # API route blueprints
│   ├── services/           # Business logic services
│   ├── static/             # Static files (CSS, JS - basic for PoC)
│   └── templates/          # HTML templates
├── tests/                  # Unit tests
│   ├── conftest.py         # Pytest fixtures
│   └── test_*.py           # Test files
├── .env                    # Local environment variables (ignored by Git)
├── .env.example            # Example environment file
├── .gitignore              # Files and directories to ignore in Git
├── init_db.py              # Script to initialize the database
├── README.md               # This file
├── requirements.txt        # Python package dependencies
└── run.py                  # Script to run the Flask application
```
