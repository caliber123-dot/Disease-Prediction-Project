# virtualenv env  
# .\env\Scripts\activate.ps1
# pip install flask
# pip install flask_sqlalchemy
# pip install gunicorn
# pip install waitress

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from waitress import serve
import pytz

app = Flask(__name__)

# import secrets
# print("your_secret_key=",secrets.token_hex(16))  # Generates a 32-character hex string
# app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
app.secret_key = "db65336f04edb23664a676f8dc3a0e17"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///disease.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class reg_tbl(db.Model):
    rg_id = db.Column(db.Integer, primary_key=True)
    rg_name = db.Column(db.String(100), nullable=False) # Cannot be NULL
    rg_email = db.Column(db.String(100), nullable=False)
    rg_phone = db.Column(db.String(50), nullable=False)
    rg_psw = db.Column(db.String(200), nullable=False)
    rg_date = db.Column(db.DateTime, default=datetime.utcnow)
    rg_status = db.Column(db.Integer, nullable=False)

class predict_tbl(db.Model):
    pr_id = db.Column(db.Integer, primary_key=True)
    pr_date = db.Column(db.DateTime, default=datetime.utcnow)
    pr_symptoms = db.Column(db.String(200), nullable=False) # Cannot be NULL
    pr_disease = db.Column(db.String(150), nullable=False)
    pr_status = db.Column(db.Integer, nullable=False)
    # pr_rg_id = db.Column(db.Integer, nullable=False)
    pr_rg_id = db.Column(db.Integer, db.ForeignKey('reg_tbl.rg_id'), nullable=False)  # Foreign Key

    # def __repr__(self) -> str:
    #     return f"{self.rg_id} - {self.rg_name}"  # Default representation
    # def get_id(self) -> str:
    #     return f"{self.rg_id}"  # Only ID
    # def get_name(self) -> str:
    #     return f"{self.rg_name}"  # Only Name
    # def get_psw(self) -> str:
    #     return f"{self.rg_psw}"  # Only Password

# app.app_context().push()
# Initialize the database
with app.app_context():
    db.create_all()

india_timezone = pytz.timezone('Asia/Kolkata')
# print(datetime.now(india_timezone))

@app.route('/')
def index():
    # all_data = Register.query.all()
    # print(all_data)
   return render_template('index.html')

@app.route('/history')
def history():
    if 'user' in session:
        flash(session['user'], 'success')
        # allTodo = predict_tbl.query.all()
        # Query all records where pr_rg_id = 1
        allTodo = predict_tbl.query.filter_by(pr_rg_id=session['user_id']).all()
        return render_template('history.html', allTodo=allTodo)
    else:
        return render_template('history.html')

@app.route('/sign_in', methods=['GET', 'POST'])  # Login Page
def sign_in():
    if request.method == 'POST':
        txtemail = request.form['txtemail']
        txtpsw = request.form['txtpsw']
        # existing_record = reg_tbl.query.filter(
        #     (reg_tbl.rg_email == txtemail) & (reg_tbl.rg_psw == txtpsw)
        # ).first()
        user = reg_tbl.query.filter_by(rg_email=txtemail).first()
        # print("GET VALUE :: ", user.rg_name)
        # if user and check_password_hash(user.get_psw(), txtpsw):
        if user and check_password_hash(user.rg_psw, txtpsw):
        # if existing_record:
            session['user_id'] = user.rg_id
            session['user'] = user.rg_name
            flash('Login successful! Hello, ' + session['user'], 'success')
            return redirect(url_for('success'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    elif 'user' in session:
        flash('Hello, ' + session['user'] , 'success')
        # return render_template('sign_in.html', username=session['user'])
    return render_template('sign_in.html')  

@app.route('/success')
def success():
    if 'user' in session:
        return render_template('predict.html', username=session['user'])
    else:
        flash('Your session has expired.', 'warning')
    return redirect(url_for('sign_in'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('sign_in'))

@app.route('/sign_up', methods=['GET', 'POST']) # Register Page
def sign_up():
    if request.method=='POST':
        txtname = request.form.get('txtname')
        txtemail = request.form.get('txtemail')
        txtphone = request.form.get('txtphone')
        txtpsw = request.form.get('txtpsw')
        txtcpsw = request.form.get('txtcpsw')
        # Check if email or phone number already exists
        existing_record = reg_tbl.query.filter(
            (reg_tbl.rg_email == txtemail) | (reg_tbl.rg_phone == txtphone)
        ).first()
        if existing_record:
            myMsg = "Record already exists with this email or phone number."
            # flash('Record already exists with this email or phone number.', 'error')
            return render_template('sign_up.html', msg=myMsg, txtname=txtname, txtemail=txtemail, txtphone=txtphone)
        else:
            # Add new record
            hashed_password = generate_password_hash(txtpsw)
            tosave = reg_tbl(
                rg_name=txtname,
                rg_email=txtemail,
                rg_phone=txtphone,
                rg_psw=hashed_password,
                rg_date=datetime.now(india_timezone),
                rg_status=1
            )
            db.session.add(tosave)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('sign_in'))
            # myMsg = "Registration successful! Please log in."
            # return render_template('sign_in.html', msg = myMsg)
    return render_template('sign_up.html')

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
        # Define the timezone
        
        tosave = predict_tbl(
                pr_date=datetime.now(india_timezone),
                pr_symptoms=symptoms_string,
                pr_disease=final_prediction,
                pr_status=1,
                pr_rg_id= session['user_id'] # Replace with a valid rg_id from reg_tbl
            )
        db.session.add(tosave)
        db.session.commit()
        flash('Record added successfully to ' + session['user'], 'success')
        # flash('Hello, ' + session['user'] , 'success')
        # Pass the dictionary to the template
        return render_template('predict.html', **symptoms, **prediction, username=session['user'])
        # if 'user' in session:
        #     return render_template('predict.html', **symptoms,**prediction , username=session['user'])
        # else:
        #     return redirect(url_for('sign_in'))
    # else:
    elif 'user' in session:
        # flash('You are already logged in!', 'success')
        flash('Hello, ' + session['user'] , 'success')
    # return render_template('predict.html')
    return redirect(url_for('success'))

if __name__ == "__main__":
    # db.create_all() 
    # app.debug = True
    # app.run(host="0.0.0.0", port=8000)
    serve(app, host="0.0.0.0", port=8000, threads=8)