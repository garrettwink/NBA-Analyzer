import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

from dataset import X_train, X_test, y_train, y_test, id_train, id_test

model = xgb.XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=7,
    random_state=42
)

model = model.fit(X_train, y_train)