# Importing libraries
# from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import statistics

# @@@@@@@ Prediction Start >> @@@@@@@@@@@@@@@
# Load and preprocess the dataset
DATA_PATH = "dataset/Training.csv"
data = pd.read_csv(DATA_PATH).dropna(axis=1)

# Check if the dataset is balanced
disease_counts = data["prognosis"].value_counts()
temp_df = pd.DataFrame({
    "Disease": disease_counts.index,
    "Counts": disease_counts.values
})

# Encode target labels
encoder = LabelEncoder()
data["prognosis"] = encoder.fit_transform(data["prognosis"])

# Split dataset into training and testing sets
X = data.iloc[:, :-1]
y = data.iloc[:, -1]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=24
)

# Train models
final_svm_model = SVC()
final_nb_model = GaussianNB()
final_rf_model = RandomForestClassifier(random_state=18)

final_svm_model.fit(X.values, y)
final_nb_model.fit(X.values, y)
final_rf_model.fit(X.values, y)

# Load test data
test_data = pd.read_csv("dataset/Testing.csv").dropna(axis=1)
test_X = test_data.iloc[:, :-1]
test_Y = encoder.transform(test_data.iloc[:, -1])

# Make predictions and combine using mode
svm_preds = final_svm_model.predict(test_X.values)
nb_preds = final_nb_model.predict(test_X.values)
rf_preds = final_rf_model.predict(test_X.values)

final_preds = [
    statistics.mode([i, j, k]) for i, j, k in zip(svm_preds, nb_preds, rf_preds)
]

# Calculate accuracy
accuracy = accuracy_score(test_Y, final_preds) * 100
print(f"Accuracy on Test dataset by the combined model: {accuracy:.2f}%")

# Create a dictionary for symptoms and prediction classes
# symptom_index = {symptom: idx for idx, symptom in enumerate(X.columns)}
symptom_index = {symptom: idx for idx, symptom in enumerate(X.columns)}

data_dict = {
    "symptom_index": symptom_index,
    "predictions_classes": encoder.classes_
}
# @@@@@@@@@@@ Prediction End >> @@@@@@@@@@@@@@@@@@@@@@@
# Predict disease based on symptoms
def predictDisease(input_symptoms):
    # Normalize input symptoms by replacing spaces with underscores
    input_symptoms = [symptom.strip().lower().replace(" ", "_") for symptom in input_symptoms.split(",")]
    input_data = [0] * len(data_dict["symptom_index"])

    # Encode symptoms into numerical format
    for symptom in input_symptoms:
        if symptom in data_dict["symptom_index"]:
            index = data_dict["symptom_index"][symptom]
            input_data[index] = 1
        else:
            print(f"Warning: Symptom '{symptom}' not recognized.")

    # Predict using trained models
    input_data = np.array(input_data).reshape(1, -1)
    rf_prediction = data_dict["predictions_classes"][final_rf_model.predict(input_data)[0]]
    nb_prediction = data_dict["predictions_classes"][final_nb_model.predict(input_data)[0]]
    svm_prediction = data_dict["predictions_classes"][final_svm_model.predict(input_data)[0]]

    # Combine predictions using mode
    final_prediction = statistics.mode([rf_prediction, nb_prediction, svm_prediction])

    return {
        "rf_model_prediction": rf_prediction,
        "naive_bayes_prediction": nb_prediction,
        "svm_model_prediction": svm_prediction,
        "final_prediction": final_prediction
    }
# Example usage
# predictions = predictDisease("Itching,Skin Rash,Nodal Skin Eruptions") #Fungal infection
# predictions = predictDisease("Continuous Sneezing,Shivering,Chills") # >>Allergy
# print(predictions)
print("Model_Optimize Code Is Running ...")
