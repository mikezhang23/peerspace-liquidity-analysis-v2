import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Create dummy models (replace with your actual trained models)
# This is just for testing - you'll use your real models

# Create a simple model
model = RandomForestRegressor(n_estimators=10, random_state=42)

# Create dummy training data
X_train = pd.DataFrame({
    'feature1': [1, 2, 3, 4, 5],
    'feature2': [2, 4, 6, 8, 10]
})
y_train = [10, 20, 30, 40, 50]

# Train the model
model.fit(X_train, y_train)

# Create a scaler
scaler = StandardScaler()
scaler.fit(X_train)

# Save the models
with open('models/liquidity_predictor.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('models/conversion_predictor.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('models/demand_forecaster.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('models/feature_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("Models saved successfully!")