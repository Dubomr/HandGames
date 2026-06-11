import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

def train_gesture_model():
    print("Loading dataset...")
    df = pd.read_csv("gesture_dataset.csv")

    X = df.drop('label', axis=1)
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("The model is being trained (Random Forest)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("-" * 30)
    print(f"Model Training Completed!")
    print(f"Accuracy Rate: %{accuracy * 100:.2f}")
    print("-" * 30)

    with open("gesture_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("The model has been saved as 'gesture_model.pkl'. You're ready to play AI Dodge!")

if __name__ == "__main__":
    train_gesture_model()