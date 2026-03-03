import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression

# Dummy training data
# [amount, category_code]
X = np.array([
    [1000, 1],
    [5000, 2],
    [200000, 1],
    [300000, 3],
    [1500, 2],
    [120000, 3]
])

# 0 = Safe, 1 = Fraud
y = np.array([0, 0, 1, 1, 0, 1])

model = LogisticRegression()
model.fit(X, y)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved")
