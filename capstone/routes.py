from fileinput import filename
import os
from pydoc import importfile
from sre_constants import SUCCESS
from flask import render_template, session, url_for, flash, redirect, request
from sqlalchemy import null
from capstone import app
from flask_mail import Message
from capstone.forms import RegistrationForm, LoginForm, classForm, importForm, resetForm, teacherForm
from capstone import db, get_db_connection, mail
from capstone.models import accounts, instructors, sections, output_schedule
from flask_login import current_user, login_required, login_user, logout_user
from capstone.scheduler import importData, main
from werkzeug.utils import secure_filename
from pathlib import Path


@app.route('/')
def home():
    return render_template('home.html', title='Home')

@app.route('/email')
def sendEmail():
    msg = Message('Testing the email stuff', 
                  sender = 'UALR.Capstone.Team42@gmail.com',
                  recipients = ['UALR.Capstone.Team42@gmail.com'])
    msg.body = "testing email stuff"
    mail.send(msg)
    return 'Message Sent!'


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print(form.errors)

    if form.validate_on_submit():
        flash(f'Registration request submitted for {form.username.data}.', 'success')

        #send email

        msg = Message('Registration Request Submitted', 
                  sender = 'UALR.Capstone.Team42@gmail.com',
                  recipients = [f'{form.email.data}'])
        msg.body = "Your registration request has been submitted."
        mail.send(msg)

        #Add to database

        username = form.username.data
        email = form.email.data
        password = form.password.data
        acc_type = form.accessLevel.data

        user = accounts(username = username, email = email, password = password, acc_type = acc_type)
        db.session.add(user)
        db.session.commit()



        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        print('valid')
        #add code to search database for email, check if email exists, and check password

        user = accounts.query.filter_by(email = form.email.data).first()
        if user and (user.password == form.password.data):
            if user.approved == True:
                login_user(user)
                if current_user.password == 'admin':
                    return redirect(url_for('reset'))
                else:
                    return redirect(url_for('hub'))

            else:
                flash('Login unsuccessful, account not approved.', 'danger')

        else:
            flash('Login unsuccessful, please check email and password.', 'danger')

    return render_template('login.html', title='Log In', form=form)



@app.route('/hub', methods=['GET', 'POST'])
@login_required
def hub():
    return render_template('hub.html', title='Hub')



@app.route('/add/instructor', methods=['GET', 'POST'])
@login_required
def addInstructor():
    if (current_user.acc_type == 'ADMIN' or current_user.acc_type == 'ROOT'):
        form=teacherForm()

        if form.validate_on_submit():
                lastName = form.lastName.data
                maxLoad = form.maxLoad.data
                disciplines = form.disciplines.data
                profAdd = instructors(LName = lastName, MaxLoad = maxLoad, Disciplines = disciplines)
                db.session.add(profAdd)
                db.session.commit()


        return render_template('addProf.html', title='Add Professor', form=form)

    else:
        flash('You must be an admin to access this page!', 'danger')
        return redirect(url_for('hub'))


@app.route('/add/section', methods=['GET', 'POST'])
@login_required
def addCourse():
    if (current_user.acc_type == 'ADMIN' or current_user.acc_type == 'ROOT'):
        form=classForm()

        if form.validate_on_submit():
            Code = form.Code.data
            Name = form.Name.data
            disciplines = form.disciplines.data
            deptCode = form.deptCode.data
            startTime = form.meetTime.data
            meetDays= form.meetingDay.data
            length = form.meetLength.data

            course = sections(Code = Code, Name = Name, Disciplines = disciplines, DepartmentCode = deptCode,StartTime=startTime, Day=meetDays, Length = length )
            db.session.add(course)
            db.session.commit()


        return render_template('addClass.html', title='Add Course', form=form)

    else:
        flash('You must be an admin to access this page!', 'danger')
        return redirect(url_for('hub'))


@app.route('/instructors')
@login_required
def instructorList():
    if (current_user.acc_type == 'ADMIN' or current_user.acc_type == 'ROOT'):
        instructorList = instructors.query.all()
        return render_template('instructors.html', title='Instructor List', instructorList=instructorList)
    
    else:
        flash('You must be an admin to access this page!', 'danger')
        return redirect(url_for('hub'))

@app.route('/sections')
@login_required
def sectionsList():
    if (current_user.acc_type == 'ADMIN' or current_user.acc_type == 'ROOT'):
        courseList = sections.query.all()
        return render_template('sections.html', title='Section list', courseList=courseList)
    else:
        flash('You must be an admin to access this page!', 'danger')
        return redirect(url_for('hub'))

#reset page
@app.route('/reset', methods=['GET', 'POST'])
@login_required
def reset():
    form=resetForm()
    if form.validate_on_submit():
        #if the form is valid and the passwords match, change the password of current user and commit to the database
        if current_user.password == form.currentPassword.data:
            if form.newPassword.data == form.confirmPassword.data:
                current_user.password = form.newPassword.data
                db.session.commit()
            else:
                flash('Old Password is incorrect or the new password does not match the confirmed password.', 'danger')
        return redirect(url_for('hub'))
    return render_template('reset.html', title = 'reset password', form=form)


@app.route('/approve', methods=['GET', 'POST'])
@login_required
def approvePage():

    if (current_user.acc_type == 'ROOT'):
        requestedAcc = accounts.query.filter_by(approved = False).first()
        
        #if the method is post, check which button was pressed
        if request.method == 'POST':
            #if the approve button was pressed go to the account for the request and set approved value to True
            if request.form['submit_button'] == 'Approve':
                print('hello')
                requestedAcc.approved = True
                db.session.commit()

                        #send email

                msg = Message('Registration Request Approved', 
                  sender = 'UALR.Capstone.Team42@gmail.com',
                  recipients = [f'{requestedAcc.email}'])
                msg.body = "Your registration request has been approved."
                mail.send(msg)
                #redirect to the same page to refresh
                return redirect(url_for('approvePage'))

            #if deny button is pressed query the database for the account with the matching email and delete that row
            elif request.form['submit_button'] == 'Deny':
                db.session.query(accounts).filter(accounts.email == requestedAcc.email ).delete()
                db.session.commit()
                msg = Message('Registration Request Denied', 
                  sender = 'UALR.Capstone.Team42@gmail.com',
                  recipients = [f'{requestedAcc.email}'])
                msg.body = "Your registration request has been denied. You may send a new registration request."
                mail.send(msg)
                #redirect to same page to refresh
                return redirect(url_for('approvePage'))


        
        return render_template('requests.html', title='Approve or Deny Registration', accountList = requestedAcc)
    
    else:
        return redirect(url_for('hub'))

@app.route('/scheduler', methods=['GET', 'POST'])
@login_required
def schedulerFunction():
    outputSchedule = output_schedule.query.all()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Generate Schedule':
            db.session.query(output_schedule).delete()
            db.session.commit()
            main()
    return render_template('schedule.html', outputSchedule = outputSchedule)






@app.route('/import', methods=['GET', 'POST'])
def importFunction():
    db.session.query(instructors).delete()
    db.session.query(sections).delete()
    db.session.commit()
    teacherPath = Path('capstone/static/instructors.dat').resolve()
    classPath = Path('capstone/static/sections.dat').resolve()
    importData(0,9, teacherPath)
    importData(1, 29, classPath)
    return redirect(url_for('hub'))



    

    



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))    
