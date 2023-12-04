from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
myapp = Flask(__name__)
myapp.secret_key = 'your_secret_key'

# Update the database URI to use SQLite
myapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
myapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(myapp)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    answers = db.relationship('StudentAnswers', backref='student', lazy=True)
    scores = db.relationship('Score', backref='student', lazy=True)

class StudentAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    answer_text = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False )
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'),nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    courses = db.relationship('Course', backref='doctor', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    questions = db.relationship('Questions', backref='courses', lazy=True)
    scores = db.relationship('Score', backref='courses', lazy=True)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    answer_id = db.relationship('StudentAnswers', backref='questions', lazy=True)

class Score(db.Model):
    sore = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True,nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'),primary_key=True, nullable=False )




@myapp.route("/")
def index():
    activeindex = "active"
    return render_template('index.html', title="Home Page", activeIndex=activeindex, session=session)

##### start doctor ######
@myapp.route("/doctor" , methods=['GET', 'POST'])
def doctorIndex():
    if 'user_id' not in session:
    # If the doctor is not logged in, redirect to the login page
        return redirect(url_for('doctorLogin'))
    activeindex = "active"
    with myapp.app_context():
            courseId = Course.query.filter_by(doctor_id = session['user_id']  ).first()

    if request.method == 'POST':
        num_questions = int(request.form['num_examples'])
        for i in range(1, num_questions+1):
            question = request.form[f'train_input_{i}']
            answer = request.form[f'train_output_{i}']

            with myapp.app_context():
                existing_question = Questions.query.filter(Questions.question==question, Questions.course_id==courseId.id).first()
            
            if existing_question is None:
                newQuestion = Questions(question=question , answer=answer , course_id=courseId.id)
                db.session.add(newQuestion)
                db.session.commit()
            else:
                flash(f"Question {i} hasn't been uploaded",'danger')
        flash(f"Questions are Uploaded Successfully to {courseId.name}",'success')
    
    return render_template('doctor/doctor.html', title="Home Page", activeIndex=activeindex, session=session , course = courseId)

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
            session['doctor_name'] = doctor.name
            # flash('Loggin in successfully','success')
            return redirect(url_for('doctorIndex'))
        else:
            flash('Invalid username or password.','danger')

    return render_template('doctor/login.html', title="Login", activeLogin=activelogin)

@myapp.route("/doctor/register", methods=['GET', 'POST'])
def doctorRegister():
    activesign = "active"
    # courses = Course.query.all()
    courses = Course.query.filter_by(doctor_id=None).all()
    if request.method == 'POST':
        name= request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        selected_option = request.form.get('course_list')

        with myapp.app_context():
            existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor is None:
            if password == confirmPassword:
                    new_doctor = Doctor(name=name, email=email, password=password)
                    db.session.add(new_doctor)
                    db.session.commit()
            else:
                flash("Password dosn't match" , 'danger')

            existing_course = Course.query.filter_by(name=selected_option).first()
            existing_course.doctor_id = new_doctor.id
            db.session.add(existing_course)
            db.session.commit()

            flash('Your Account is created successfully!','success')
            return redirect(url_for('doctorLogin'))

        else:
            flash('Your Account already exists!','danger')
            return redirect(url_for('doctorLogin'))

    return render_template('doctor/signup.html', title='Sign up', activeSign=activesign, courses = courses)

@myapp.route("/doctor/scores", methods=['GET'])
def studentScores():
    course = Course.query.filter_by( doctor_id = session['user_id'] ).first()
    scores = Score.query.filter_by( course_id = course.id ).all()
    students = []
    
    for score in scores:
        student = Student.query.filter_by( id = score.student_id ).first()
        students.append(student)

    combined_data = zip(students , scores)

    return render_template( 'doctor/student-scores.html' , combined_data = combined_data , course = course )


##### end doctor ######



##### Start Student ######

@myapp.route("/student", methods=['GET', 'POST'])
def studentIndex():
    if 'user_id' not in session:
        # If the student is not logged in, redirect to the login page
        return redirect(url_for('studentLogin'))
    activeindex = "active"

    with myapp.app_context():
        existing_student = Student.query.filter_by(id = session['user_id']).first()
        courses = Course.query.all()

    return render_template('student/student.html', title="Home Page", activeIndex=activeindex, session=session,courses=courses )

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
        confirmPassword = request.form['confirmPassword']

        with myapp.app_context():
            existing_user = Student.query.filter_by(email=email).first()

        if existing_user is None:
            if password == confirmPassword :
                new_user = Student(name=name,email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                flash('Account is created successfully', 'success')
                return redirect(url_for('studentLogin'))
            else:
                flash("Password doesn't match", 'danger')
        else:
            flash('Your Account already exists!','danger')
            return redirect(url_for('studentLogin'))

    return render_template('student/signup.html', title='Sign up', activeSign=activesign)


@myapp.route("/student/<int:stu_id>/viewScore")
def viewScore(stu_id):
    scores = Score.query.filter_by( student_id = stu_id ).all()
    courses_names = []
    for score in scores:
        course = Course.query.get(score.course_id)
        if course:
            courses_names.append(course.name)
    print(courses_names)
    return render_template('student/viewScore.html' , title = 'Score' , scores=scores , courses=courses_names )

@myapp.route('/course/<int:course_id>', methods=['GET','POST'])
def course_details(course_id):
    course = Course.query.get(course_id)
    questions = Questions.query.filter(Questions.course_id==course.id)
    unanswered_questions= []
    answered_questions= []
    answers = []
    combined_data = None

    for question in questions:
        existing_answer = StudentAnswers.query.filter( StudentAnswers.question_id==question.id, StudentAnswers.student_id == session['user_id'] ).first()
        if existing_answer is None:
            unanswered_questions.append(question)
        else:
            answers.append(existing_answer)
            answered_questions.append(question)

    if answers and answered_questions:
        combined_data = zip(answered_questions, answers)

    if request.method == "POST":
        for i,question in enumerate(unanswered_questions):
            new_answer = StudentAnswers( answer_text=request.form[f'question_{i+1}']  , question_id = question.id , student_id = session['user_id']  )
            db.session.add(new_answer)
            db.session.commit()
        flash('Your Answers are submitted successfully', 'success')
        return redirect( url_for( 'course_details', course_id=course_id ) )

    if course:
        return render_template('student/course-details.html',title = course.name, course=course , unanswered_questions = unanswered_questions , combined_data = combined_data)
    else:
        flash("Course Not found !!!" , 'danger')
        # return render_template('course_not_found.html')

##### End Student ######


# @myapp.route('/courses', methods=["GET" , "POST"])
# def courseList():
#     courses = Course.query.all()
#     existing_course = Course.query.filter_by(name = 'Web Development').first()
#     selected_option= ''
#     if request.method == "POST":
#         selected_option = request.form.get('course_list')
#         existing_course.doctor_id = 4
#         db.session.add(existing_course)
#         db.session.commit()

    # return render_template("courses.html", courses = courses , selected = selected_option)


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
