from flask import Flask, render_template, flash, request, redirect
import sqlite3
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user
from forms import LoginForm
import os

app = Flask(__name__)
app.debug = True

login_manager = LoginManager(app)
login_manager.login_view = "login"
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = str(id)
        self.username = username
        self.password = password
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('login.db')
    curs = conn.cursor()
    curs.execute("SELECT * FROM login WHERE user_id = ?", [user_id])
    lu = curs.fetchone()
    conn.close()
    if lu is None:
        return None
    else:
        return User(int(lu[0]), lu[1], lu[3], lu[2])

@app.route("/")
def home():
    return redirect("/login")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/userDic", methods=['GET', 'POST'])
def userDic():
    connection = sqlite3.connect("login.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM login")
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in data]
    connection.close()

    return(result)

@app.route("/registerAcc", methods=['GET', 'POST'])
def registerAcc():
    try:
        userEmail = request.form['email']
        userPassword = request.form['password']
        userName = request.form['username']

        addDB = "INSERT INTO login (username, email, password) VALUES (?, ?, ?)"
        conn = sqlite3.connect('login.db')
        cursor = conn.cursor()
        cursor.execute(addDB, (userName, userEmail, userPassword))
        conn.commit()
        conn.close()

        return redirect("/login")
    except Exception as e:
        # Handle the exception, e.g., log the error or return an error page
        return "An error occurred during registration."

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/profile")
    
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('login.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM login WHERE username = ?", [form.username.data])
        user = curs.fetchone()
        conn.close()

        if user and form.username.data == user[1] and form.password.data == user[3]:
            Us = load_user(user[0])
            login_user(Us, remember=form.remember.data)
            flash('Logged in successfully ' + form.username.data)
            return redirect('/profile')
        else:
            flash('Login Unsuccessful.')

    return render_template('login.html', title='Login', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, threaded=True)
