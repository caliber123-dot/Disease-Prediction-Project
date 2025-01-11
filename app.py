# virtualenv env  
# .\env\Scripts\activate.ps1
# pip install flask
# pip install flask_sqlalchemy
# pip install gunicorn
# pip install waitress

from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from waitress import serve


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///disease.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

class reg_tbl(db.Model):
    rg_id = db.Column(db.Integer, primary_key=True)
    rg_name = db.Column(db.String(100), nullable=False) # Cannot be NULL
    rg_phone = db.Column(db.String(50), nullable=False)
    rg_email = db.Column(db.String(100), nullable=False)
    rg_psw = db.Column(db.String(50), nullable=False)
    rg_date = db.Column(db.DateTime, default=datetime.utcnow)
    rg_status = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f"{self.rg_id} - {self.rg_name}"
    

# @app.route('/')
# def start():
#     return '<h1>This is Home Page 1</h1>'

@app.route('/')
def index():
    # all_data = Register.query.all()
    # print(all_data)
   return render_template('index.html')

from model_optimize import predictDisease
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method=='POST':
        # Retrieve form data
        ddlsymtom1 = request.form.get('ddlsymtom1')
        ddlsymtom2 = request.form.get('ddlsymtom2')
        ddlsymtom3 = request.form.get('ddlsymtom3')
        ddlsymtom4 = request.form.get('ddlsymtom4')
        ddlsymtom5 = request.form.get('ddlsymtom5')
        # Retrieve form data and store it in the dictionary
        symptoms = {
            "s1": ddlsymtom1,
            "s2": ddlsymtom2,
            "s3": ddlsymtom3,
            "s4": ddlsymtom4,
            "s5": ddlsymtom5,
        }
        # Filter and include specific strings
        disallowed_values = {"Choose Symptom1", "Choose Symptom2", "Choose Symptom3", "Choose Symptom4", "Choose Symptom5"}  # Add ! allowed values here
        # Filter out disallowed values
        filtered_values = [value for value in symptoms.values() if value and value not in disallowed_values]
        # Join the filtered values into a single string
        symptoms_string = ",".join(filtered_values)
        # print(symptoms_string)
        
        predictions = predictDisease(symptoms_string ) # Call to Predictions to Get Result
        # result = predictDisease("Itching,Skin Rash,Nodal Skin Eruptions")
        # print("Predicted Disease:", predictions["final_prediction"])
        
        rf_prediction = predictions['rf_model_prediction']
        nb_prediction = predictions['naive_bayes_prediction']
        svm_prediction = predictions['svm_model_prediction']
        final_prediction = predictions['final_prediction']
        # print(final_prediction)
        prediction = {
            "rf_prediction": rf_prediction,
            "nb_prediction": nb_prediction,
            "svm_prediction": svm_prediction,
            "final_prediction": final_prediction,
        }
        # Pass the dictionary to the template
        return render_template('predict.html',**symptoms,**prediction)
    return render_template('predict.html')



if __name__ == "__main__":
    # db.create_all() 
    # app.debug = True
    # app.run(host="0.0.0.0", port=8000)
    # pip install waitress
    serve(app, host="0.0.0.0", port=8000, threads=8)