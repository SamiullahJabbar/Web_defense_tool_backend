import joblib
import numpy as np

xgb_model = joblib.load("ml_engine/xgboost_model.pkl")
lgbm_model = joblib.load("ml_engine/lightgbm_model.pkl")

def predict_with_xgboost(input_data):
    input_array = np.array(input_data).reshape(1, -1)
    prediction = xgb_model.predict(input_array)
    probability = xgb_model.predict_proba(input_array)[0][1]  
    return {
        "model": "XGBoost",
        "prediction": int(prediction[0]),
        "attack_probability": round(probability, 4)
    }

def predict_with_lightgbm(input_data):
    input_array = np.array(input_data).reshape(1, -1)
    probability = lgbm_model.predict(input_array)[0]
    prediction = 1 if probability >= 0.5 else 0
    return {
        "model": "LightGBM",
        "prediction": prediction,
        "attack_probability": round(probability, 4)
    }

test_sample = [250, 0.3, 1, 7] 

xgb_result = predict_with_xgboost(test_sample)
lgbm_result = predict_with_lightgbm(test_sample)

print("\n✅ Prediction using XGBoost:", xgb_result)
print("✅ Prediction using LightGBM:", lgbm_result)
