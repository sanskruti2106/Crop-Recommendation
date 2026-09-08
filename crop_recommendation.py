import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("Crop_recommendation.csv")

print("Dataset loaded successfully!")
print("Shape:", df.shape)
print(df.head())

# Features and target
X = df.drop("label", axis=1)
y = df["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Test
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

# Crop prediction
sample = pd.DataFrame([[
    32,
    46,
    23,
    26,
    80,
    6.5,
    200
]], columns=[
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
])

prediction = model.predict(sample)

print("Recommended Crop:", prediction[0])
print("\n===== CROP RECOMMENDATION =====")

N = float(input("Enter Nitrogen (N): "))
P = float(input("Enter Phosphorus (P): "))
K = float(input("Enter Potassium (K): "))
temperature = float(input("Enter Temperature: "))
humidity = float(input("Enter Humidity: "))
ph = float(input("Enter pH: "))
rainfall = float(input("Enter Rainfall: "))

user_data = pd.DataFrame([[
    N, P, K, temperature, humidity, ph, rainfall
]], columns=[
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
])

result = model.predict(user_data)

print("\n🌾 Recommended Crop:", result[0])