"""Flask app for notes"""

from flask import Flask, jsonify, request, render_template, session, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Note

from forms import AddUserForm, LoginUserForm, AddNoteForm, EditNoteForm

# from env import USER_POSTGRES, PASSWORD_POSTGRES

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///users'

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
    """Home page, redirects to registration form"""
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Shows and handles user registration form"""

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

        return redirect(f"/users/{user.username}")

    else:

        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Log in and authenticate user"""

    form = LoginUserForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username=username,
            password=password)

        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Bad Name / Bad Password']

    return render_template("login.html", form=form)

@app.route("/users/<username>")
def show_user_page(username):
    """Shows user info and their posts"""

    if 'username' in session:
        if username == session["username"]:
            user = User.query.filter_by(username=username).first()
            return render_template('user_page.html',
                                   username=user.username,
                                   first_name=user.first_name,
                                   last_name=user.last_name,
                                   email=user.email,
                                   notes=user.notes)

    flash('You Must Be Logged In To View That Page!')
    return redirect("/")

@app.route("/logout")
def logout():
    """Logs user out"""

    session.pop('username', None)

    return redirect("/")

@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def show_note_form(username):
    """Show and handle note form"""

    form = AddNoteForm()

    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner=user.username)

        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{user.username}")
    else:
        return render_template("note_form.html", form=form)


@app.route("/notes/<int:note_id>/update", methods=["GET", "POST"])
def show_edit_note_form(note_id):
    """ Show and handle edit note form"""

    note = Note.query.get_or_404(note_id)

    form = EditNoteForm(obj=note)

    user = note.user

    if user.username != session['username']:
        flash("You are trying to edit a note that is not yours")
        return redirect("/")

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note.title = title
        note.content = content

        flash("Edit Successful!")
        db.session.commit()

        return redirect(f"/users/{user.username}")

    else:
        return render_template("update_note.html", form=form, note=note)

@app.route("/notes/<int:note_id>/delete", methods=["POST"])
def delete_note(note_id):
    """ Delete note """

    note = Note.query.get_or_404(note_id)

    user = note.user

    if user.username != session['username']:
        flash("You are trying to delete a note that is not yours")
        return redirect("/")

    db.session.delete(note)
    db.session.commit()

    flash("Note sucessfully deleted")

    return redirect(f"/users/{user.username}")

@app.route("/users/<username>/delete", methods=["POST"])
def delete_account(username):
    """ Delete account"""

    user = User.query.get_or_404(username)

    if user.username != session['username']:
        flash("You are trying to delete a note that is not yours")
        return redirect("/")

    Note.query.filter_by(owner=user.username).delete()
    session.pop('username', None)
    db.session.delete(user)

    db.session.commit()

    flash("User successfuly deleted")
    return redirect("/")

