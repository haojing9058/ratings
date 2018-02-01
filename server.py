"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # return "<html><body>Placeholder for the homepage.</body></html>"

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():
    """A form ask for email address and password
    and a form that shows the registration form"""

    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Process the registration form, checking to see if a user with
    that email address exists, and if not, creating a new user in that
    database"""

    email = request.form.get("email")
    password = request.form.get("password")

    check_email = User.query.filter_by(email=email).first()

    if check_email:
        check_password = User.query.filter(User.email==email, User.password==password).first()
        if check_password:
            flash("You're logged in!")
            return redirect("/user/user_id")
        else:
            flash("wrong password!")
            return redirect("/")

    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    return redirect("/")


@app.route("/logout")
def log_out():
    """Log out the user"""

    db.session.remove()
    flash("Logged out")
    return redirect("/")


@app.route("/users/<user_id>")
def display_user(user_id):
    """Display informationa about a particular user"""

    user_details = User.query.filter(User.user_id==user_id).first()

    user_ratings = Rating.query.filter(Rating.user_id==user_id).all()

    user_movies = []
    for r in user_ratings:
        movie = Movie.query.get(r.movie_id).title
        score = r.score
        user_movies.append((movie, score))

    return render_template("user_info.html",
                           user_details=user_details,
                           user_movies=user_movies)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
