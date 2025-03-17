import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Load dataset
data = pd.read_csv('ml_engine/supervised_request_logs.csv')

# Features and target
X = data[['request_count', 'avg_interval', 'method_code', 'path_depth']]
y = data['label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Define LightGBM classifier
model = lgb.LGBMClassifier(
    objective='binary',
    boosting_type='gbdt',
    learning_rate=0.1,
    num_leaves=31,
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
y_pred_probs = model.predict_proba(X_test)[:, 1]

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print("\n✅ LightGBM Model Training Completed")
print("Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Save model
joblib.dump(model, "ml_engine/lightgbm_model.pkl")
print("\n✅ LightGBM model saved at ml_engine/lightgbm_model.pkl")
