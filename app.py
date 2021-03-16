"""Flask app for notes"""

from flask import Flask, jsonify, request, render_template, session, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User

from forms import AddUserForm, LoginUserForm

# from env import USER_POSTGRES, PASSWORD_POSTGRES

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes'

#Windows database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{USER_POSTGRES}:{PASSWORD_POSTGRES}@127.0.0.1/users"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route("/")
def home():


    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_page():

    form = AddUserForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username=username, 
            password=password, 
            email=email, 
            first_name=first_name, 
            last_name=last_name)

        db.session.add(user)
        db.session.commit()

        session['username'] = user.username

        return redirect("/secret")

    else:

        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_page():

    form = LoginUserForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username=username, 
            password=password)

        if user:
            session['username'] = user.username
            return redirect("/secret")
        else:
            form.username.errors = ['Bad Name / Bad Password']
        
    return render_template("login.html", form=form)

@app.route("/secret")
def secret_page():

    if 'username' in session:
        return render_template("secret.html")    


    flash('You Must Be Logged In To View That Page!')   
    return redirect("/")

@app.route("/logout")
def logout():

    session.pop('username', None)

    return redirect("/")




