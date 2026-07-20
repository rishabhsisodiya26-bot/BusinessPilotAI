import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from datetime import timedelta

class SalesForecaster:
    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        self.feature_cols = []
        self.is_trained = False

    def _prepare_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Creates lag features and datetime attributes for forecasting.
        """
        df = df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        # DateTime components
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['Month'] = df['Date'].dt.month
        df['DayOfYear'] = df['Date'].dt.dayofyear
        
        # Lag features (revenue from 7 days ago, 14 days ago, and 30 days ago)
        df['Lag_7'] = df['Revenue'].shift(7)
        df['Lag_14'] = df['Revenue'].shift(14)
        
        # Rolling averages
        df['Roll_7_Mean'] = df['Revenue'].shift(1).rolling(window=7).mean()
        df['Roll_30_Mean'] = df['Revenue'].shift(1).rolling(window=30).mean()
        
        # Drop rows with NaN due to shift/rolling
        if is_training:
            df = df.dropna().reset_index(drop=True)
        else:
            # Impute NaN lags with overall mean for testing/inference
            df = df.bfill().fillna(df['Revenue'].mean())
            
        return df

    def train(self, df: pd.DataFrame):
        """
        Trains the forecasting model.
        """
        if len(df) < 35:
            raise ValueError("Insufficient data points. Minimum 35 historical sales records are required.")
            
        prepared_df = self._prepare_features(df, is_training=True)
        
        self.feature_cols = ['DayOfWeek', 'Month', 'DayOfYear', 'Lag_7', 'Lag_14', 'Roll_7_Mean', 'Roll_30_Mean']
        
        X = prepared_df[self.feature_cols]
        y = prepared_df['Revenue']
        
        # Split train/test (last 30 days as test)
        split_idx = len(prepared_df) - 30
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        predictions = self.model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # Refit on all data
        self.model.fit(X, y)
        self.is_trained = True
        
        metrics = {
            "MSE": float(mse),
            "RMSE": float(np.sqrt(mse)),
            "MAE": float(mae),
            "R2": float(r2)
        }
        
        return metrics

    def predict_future(self, historical_df: pd.DataFrame, days_to_forecast: int = 30) -> pd.DataFrame:
        """
        Forecasts future revenue daily.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")
            
        # Get last 45 records to build lags
        df = historical_df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').tail(45).reset_index(drop=True)
        
        future_dates = []
        future_predictions = []
        
        current_last_date = df['Date'].max()
        
        for i in range(1, days_to_forecast + 1):
            next_date = current_last_date + timedelta(days=i)
            
            # Temporary row
            new_row = {
                'Date': next_date,
                'Revenue': 0.0, # Placeholder
                'OrdersCount': 0,
                'InventoryLevel': 0
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Prepare features for the whole frame
            prepared = self._prepare_features(df, is_training=False)
            
            # Predict the last row
            last_feat = prepared[self.feature_cols].tail(1)
            pred_val = float(self.model.predict(last_feat)[0])
            
            # Update the revenue value in the dataframe so it feeds subsequent lags
            df.loc[df.index[-1], 'Revenue'] = pred_val
            
            future_dates.append(next_date.strftime("%Y-%m-%d"))
            future_predictions.append(round(pred_val, 2))
            
        return pd.DataFrame({
            "Date": future_dates,
            "ForecastedRevenue": future_predictions
        })
