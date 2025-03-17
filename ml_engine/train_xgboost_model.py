import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

print("🔥 Script Started")

try:
    # Load dataset with correct relative path
    dataset_path = os.path.join(os.path.dirname(__file__), 'supervised_request_logs.csv')
    print(f"📂 Loading dataset from: {dataset_path}")
    data = pd.read_csv(dataset_path)

    # Define features and target
    X = data[['request_count', 'avg_interval', 'method_code', 'path_depth']]
    y = data['label']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Define XGBoost classifier
    model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        eval_metric='logloss',
        random_state=42
    )

    # Train the model
    print("🔍 Training XGBoost model...")
    model.fit(X_train, y_train)

    # Predict on test data
    y_pred = model.predict(X_test)

    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    print("\n✅ XGBoost Model Training Completed")
    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'xgboost_model.pkl')
    joblib.dump(model, model_path)
    print(f"\n✅ XGBoost model saved at {model_path}")

except Exception as e:
    print(f"❌ Error occurred: {e}")
