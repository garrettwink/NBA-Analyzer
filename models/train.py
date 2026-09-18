import xgboost as xgb
from sklearn.metrics import mean_squared_error
import pandas as pd

from dataset import X_train, X_test, y_train, y_test, id_train, id_test

model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective='reg:squarederror',
    random_state=42
)

model = model.fit(X_train, y_train)