from ..models import db, PredictorStockData, Product
from sqlalchemy import desc
import pandas as pd # For PoC, let's assume pandas can be used

def add_predictor_data_entry(data):
    product = Product.query.get(data['product_id'])
    if not product:
        return None, "Product not found"

    entry = PredictorStockData(
        product_id=data['product_id'],
        date=data['date'], # Expecting YYYY-MM-DD string, SQLAlchemy handles conversion for Date type
        units_sold=data['units_sold'],
        avg_sale_price=data.get('avg_sale_price'),
        promotion_active=data.get('promotion_active', False),
        special_event=data.get('special_event')
    )
    db.session.add(entry)
    db.session.commit()
    return entry, None

def get_predictor_data_for_product(product_id):
    return PredictorStockData.query.filter_by(product_id=product_id).order_by(PredictorStockData.date).all()

def predict_stock_simple_moving_average(product_id, periods_to_predict=3, window_size=3):
    historical_data = PredictorStockData.query.filter_by(product_id=product_id)                                               .order_by(PredictorStockData.date)                                               .all()
    if not historical_data or len(historical_data) < window_size:
        return None, "Not enough historical data for prediction with current window size."

    # Use pandas for easier manipulation if available and allowed for PoC
    # For now, manual calculation:
    sales_values = [hd.units_sold for hd in historical_data]

    predictions = []

    # Simple Moving Average
    # To predict the next period, average the last 'window_size' actuals
    # For subsequent periods, we'd ideally use predicted values if actuals aren't available,
    # but for a simple PoC, let's just project based on the last known actuals.

    if len(sales_values) >= window_size:
        # Predict future periods
        current_values_for_sma = list(sales_values) # Make a mutable copy
        for i in range(periods_to_predict):
            if len(current_values_for_sma) < window_size:
                # Not enough data to form a full window for prediction
                # Could use a smaller window, or stop, or use last known prediction
                # For PoC, let's use the average of whatever is left if less than window_size
                if not current_values_for_sma: # no data left
                    predicted_value = 0 # or some other default
                else:
                    predicted_value = sum(current_values_for_sma[-len(current_values_for_sma):]) / len(current_values_for_sma)

            else: # We have enough data for a full window
                sma = sum(current_values_for_sma[-window_size:]) / window_size
                predicted_value = round(sma) #

            predictions.append({'period': i + 1, 'predicted_units_sold': predicted_value})
            # For a true rolling forecast, you'd append the prediction to current_values_for_sma
            # to predict the next step. For simplicity here, we are doing fixed window from original data.
            # Let's refine: Use the most recent 'window_size' data points for each prediction step,
            # and for subsequent steps, if we were doing a multi-step forecast where each step
            # depends on the prior, we'd add the prediction.
            # For this PoC, let's assume each future period's prediction is based on the *original* last window.

        # Re-evaluating the simple SMA for multi-period:
        # A common way for multi-step is to predict one step, then use that prediction as input for the next.
        # Or, more simply, assume the conditions that led to the last SMA persist.
        # Let's use a simple approach: the SMA of the *last available actual data* is the prediction for all future periods requested.

        last_window_sma = sum(sales_values[-window_size:]) / window_size
        predictions = []
        for i in range(periods_to_predict):
            predictions.append({'period': i + 1, 'predicted_units_sold': round(last_window_sma)})

        return predictions, None
    else: # Not enough data for even one SMA calculation
        return None, "Not enough historical data to calculate initial SMA."
