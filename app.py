
# import pandas
import smtplib
import sqlite3, os
from flask_mail import Mail, Message
from flask import Flask, redirect, render_template, request, url_for, session, redirect, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash , check_password_hash

app = Flask(__name__)

mail = Mail(app)


#   CONFIGURING THE SECRET KEY 
app.config['SECRET_KEY']=os.urandom(24)


##########################################
#####   MAIL CONFIGURATION     #######
########################################## 
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'BestMotoServ@outlook.com'
app.config['MAIL_PASSWORD'] = 'MotoServ'



##########################################
#####   DATABASE CONFIGURATIONS    #######
########################################## 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Gsandanat.1'
app.config['MYSQL_DB'] = 'GarageDB'
 

db = MySQL(app)

##################################################################
###### FUNCTION THAT HOLD THE CURRENT USER IN THE SESSION ########
##################################################################
def current_user():
    
    logged_user = None
    
    if 'user' in session:
        user = session['user']

        user_cur = db.connection.cursor()
        user_cur.execute("SELECT * FROM car_owner WHERE OwnerID = %s", [user])
        logged_user = user_cur.fetchone()

    return logged_user


##################################################################
###### FUNCTION THAT HOLD THE CURRENT STAFF MEMBER IN THE SESSION ########
##################################################################
def current_staff():
    
    logged_staff = None
    
    if 'staff' in session:
        staff = session['staff']

        staff_cur = db.connection.cursor()
        staff_cur.execute("SELECT * FROM staff_credentials WHERE OwnerID = %s", [staff])
        logged_staff = staff_cur.fetchone()

    return logged_staff

###############################################################################################


@app.route('/')
def home():
    user = current_user()
    return render_template("index.html", user = user)

@app.route('/about')
def about():
    user = current_user()
    return render_template('about.html', user = user)

###############################################################################

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    user = current_user()

    if request.method == 'POST':

        name = request.form.get('fullname')
        email = request.form.get('email')
        message = request.form.get('message')
        phone = request.form.get('phone')
        msg = Message(subject=f'mail from {name}',
                      body = f"Name: {name} \n email: {email} \n Phone: {phone} \n\n\n {message}",
                      sender = email,
                      recipients = 'BestMotoServ@outlook.com')

        mail.send(msg)
        return render_template('contacts.html', success = True)

    return render_template('contacts.html', user = user)

####################################################################

@app.route('/services') 
def services():
    user = current_user()
    return render_template('services.html', user = user)


#######################################################
###################   LOGIN ROUTE  ####################
#######################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = current_user()
    staff = current_staff()
    error = None
    if request.method == 'POST':

        username = request.form.get('email')
        password = request.form.get('password')

        #   Creating a connection cursor
        user_cur = db.connection.cursor()
        staff_cur = db.connection.cursor()

         #   select the user from the database
        user_cur.execute("SELECT * FROM car_owner WHERE Email= %s", [username])
        staff_cur.execute("SELECT * FROM Staff_credentials WHERE Email=%s", [username])

        #   fetch the user
        logged_user = user_cur.fetchone()
        logged_staff = staff_cur.fetchone()

################################################################################################

 #   check if the staff credentials exists in database
        if logged_staff:

            #   check if the password entered match with the password in the database
            if (logged_staff[2], password):

                #   create a session
                session['staff'] = logged_staff[0]    #   keeps the user by ID in the session

                flash(f"Hello {logged_staff[1]}. You've logged in as a administrator!", category='success')
                return redirect(url_for('home'))
            else:
                error = "The password is incorrect"
                flash("Something went wrong! Make sure you are using the correct username and password.", category='error')
              
        else:
            error = "Username is incorect"
     


################################################################################################

        #   check if the user exists in database
        if logged_user:

            #   check if the password entered match with the password in the database
            if check_password_hash(logged_user[-2], password):

                #   create a session
                session['user'] = logged_user[0]    #   keeps the user by ID in the session

                flash(f"Hello {logged_user[1]}. You've logged in successfully!", category='success')
                return redirect(url_for('home'))
            else:
                error = "The password is incorrect"
                flash("Something went wrong! Make sure you are using the correct username and password.", category='error')
              
        else:
            error = "Username is incorect"
     

    return render_template('login.html', user = user, error = error)

#################################################################################################


#######################################################
################   REGISTER ROUTE  ####################
#######################################################
@app.route('/register', methods = ['GET', 'POST'])
def register():
    user = current_user()
    if request.method == 'POST':
        FName = request.form.get('FName')
        LName = request.form.get('LName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        hashed_pass = generate_password_hash(request.form.get('password'), method='sha256')
        conf_hashed_pass = generate_password_hash(request.form.get('conf_password'), method='sha256')

        #   Check the credentials rules
    
        if len(request.form.get('password')) < 7:
            flash("Password must be at least 7 charactaers", category = 'error')

        elif request.form.get('password') != request.form.get('conf_password'):
            flash("Passwords do not match", category = 'error')

        else:

            #   Creating a connection cursor
            user_cur = db.connection.cursor()

            #   Executing SQL Statements
            user_cur.execute("INSERT INTO car_owner (FName, LName, Email, Tel, Pass, Conf_pass)\
                            VALUES (%s, %s, %s, %s, %s, %s)", (FName, LName, email, phone, hashed_pass, conf_hashed_pass))

            #   Saving the actions performed on the DB
            db.connection.commit()
            
            #   Closing the cursor
            user_cur.close()

            session['user'] = FName

            flash(f"Hello {FName}. Your account has been created successfuly. Please log in to your account.", category = 'success')

            return redirect(url_for('login'))


    return render_template('register.html', user = user)

######################################################################

@app.route('/accidentAdvices')
def accidentAdvices():
    user = current_user()
    return render_template('accidentAdvices.html', user = user)


@app.route('/maintenanceTips')
def tips():
    user = current_user()
    return render_template('carmaintenancetips.html', user = user)

#######################################################
#################  BOOK SERVICE ROUTE  ################
#######################################################
@app.route('/bookService', methods = ['GET', 'POST'])
def bookService():
    user = current_user()
    if request.method == 'POST':
        carDetails  = request.form
        Manufacturer = carDetails['Manufacturer']
        Model = carDetails['Model']
        RegYear = carDetails['RegYear']
        Reg_number = carDetails['Reg_number']

        #   Creating a connection cursor
        cursor = db.connection.cursor()

        #   Executing SQL Statements
        cursor.execute("INSERT INTO vehicle (Manufacturer, Model, RegYear, Reg_number)\
                        VALUES (%s, %s, %s, %s)", (Manufacturer, Model, RegYear, Reg_number))

        #   Saving the actions performed on the DB
        db.connection.commit()
        
        #   Closing the cursor
        cursor.close()

    return render_template('bookservice.html', user = user)


@app.route('/help')
def helpPage():
    user = current_user()
    return render_template('askforhelp.html', user = user)

@app.route('/logout')
def logout():
    session.pop('user', None)

    flash("You have been logged out. We are waiting for you again.", category="success")
    return redirect(url_for('home'))


if __name__=="__main__":
    app.run(debug=True)