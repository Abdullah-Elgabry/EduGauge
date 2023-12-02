from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy

myapp = Flask(__name__)
myapp.secret_key = 'your_secret_key'

# Update the database URI to use SQLite
myapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
myapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(myapp)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Doctor(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)


@myapp.route("/")
def index():
    activeindex = "active"
    return render_template('index.html', title="Home Page", activeIndex=activeindex, session=session)

##### start doctor ######
@myapp.route("/doctor")
def doctorIndex():
    if 'user_id' not in session:
    # If the doctor is not logged in, redirect to the login page
        return redirect(url_for('doctorLogin'))
    activeindex = "active"
    return render_template('doctor/doctor.html', title="Home Page", activeIndex=activeindex, session=session)

@myapp.route("/doctor/login", methods=['GET', 'POST'])
def doctorLogin():
    activelogin = "active"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with myapp.app_context():
            doctor = Doctor.query.filter_by(email=email, password=password).first()

        if doctor:
            session['user_id'] = doctor.id
            session['doctor_name'] = doctor.email
            # flash('Loggin in successfully','success')
            return redirect(url_for('doctorIndex'))
        else:
            flash('Invalid username or password.','danger')

    return render_template('doctor/login.html', title="Login", activeLogin=activelogin)

@myapp.route("/doctor/register", methods=['GET', 'POST'])
def doctorRegister():
    activesign = "active"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with myapp.app_context():
            existing_doctor = Doctor.query.filter_by(email=email).first()

        if existing_doctor is None:
            new_doctor = Doctor(email=email, password=password)
            db.session.add(new_doctor)
            db.session.commit()
            flash('Account is created successfully', 'success')
            return redirect(url_for('doctorLogin'))
        else:
            flash('Your Account already exists!','danger')
            return redirect(url_for('doctorLogin'))

    return render_template('doctor/signup.html', title='Sign up', activeSign=activesign)

##### end doctor ######



##### Start Student ######

@myapp.route("/student")
def studentIndex():
    if 'user_id' not in session:
        # If the doctor is not logged in, redirect to the login page
        return redirect(url_for('studentLogin'))
    activeindex = "active"
    return render_template('student/student.html', title="Home Page", activeIndex=activeindex, session=session)

@myapp.route("/student/login", methods=['GET', 'POST'])
def studentLogin():
    activelogin = "active"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with myapp.app_context():
            user = Student.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            # flash('Loggin in successfully','success')
            return redirect(url_for('studentIndex'))
        else:
            flash('Invalid username or password.','danger')

    return render_template('student/login.html', title="Login", activeLogin=activelogin)

@myapp.route("/student/register", methods=['GET', 'POST'])
def studentRegister():
    activesign = "active"
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        with myapp.app_context():
            existing_user = Student.query.filter_by(email=email).first()

        if existing_user is None:
            new_user = Student(name=name,email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account is created successfully', 'success')
            return redirect(url_for('studentLogin'))
        else:
            flash('Your Account already exists!','danger')
            return redirect(url_for('studentLogin'))

    return render_template('student/signup.html', title='Sign up', activeSign=activesign)


@myapp.route("/student/viewScore")
def viewScore():
    return render_template('student/viewScore.html' , title = 'Score')
##### End Student ######


@myapp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    if (session.get('doctor_name')):
        session.pop('doctor_name',None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with myapp.app_context():
        db.create_all()
    myapp.run(debug=True, port=9000)
