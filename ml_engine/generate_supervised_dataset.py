import pandas as pd
import numpy as np
import random


rows = 1000

normal_request_count = np.random.randint(1, 100, size=int(rows * 0.7))
normal_avg_interval = np.round(np.random.uniform(1.0, 10.0, size=int(rows * 0.7)), 2)
normal_method_code = np.random.choice([0, 1], size=int(rows * 0.7))  # 0=GET, 1=POST
normal_path_depth = np.random.randint(1, 5, size=int(rows * 0.7))
normal_label = np.zeros(int(rows * 0.7))

attack_request_count = np.random.randint(150, 500, size=int(rows * 0.3))
attack_avg_interval = np.round(np.random.uniform(0.01, 1.0, size=int(rows * 0.3)), 2)
attack_method_code = np.random.choice([0, 1], size=int(rows * 0.3))
attack_path_depth = np.random.randint(5, 10, size=int(rows * 0.3))
attack_label = np.ones(int(rows * 0.3))
request_count = np.concatenate((normal_request_count, attack_request_count))
avg_interval = np.concatenate((normal_avg_interval, attack_avg_interval))
method_code = np.concatenate((normal_method_code, attack_method_code))
path_depth = np.concatenate((normal_path_depth, attack_path_depth))
labels = np.concatenate((normal_label, attack_label))
data = pd.DataFrame({
    'request_count': request_count,
    'avg_interval': avg_interval,
    'method_code': method_code,
    'path_depth': path_depth,
    'label': labels
})

data = data.sample(frac=1).reset_index(drop=True)
data.to_csv('ml_engine/supervised_request_logs.csv', index=False)
print("✅ Supervised dataset generated at ml_engine/supervised_request_logs.csv")
