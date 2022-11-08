
from flask import Flask, render_template, url_for, flash, redirect, current_app, session, request
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


app = Flask(__name__)
app.config["SECRET_KEY"] = "13980cda3a69e6094cc5dd5bb1035e89"

#linking database
SQLALCHEMY_DATABASE_URI = ("mysql+mysqlconnector://{0}:{1}@{2}/{3}".format("anyab", "wordledatabase", "anyab.mysql.pythonanywhere-services.com", "anyab$dbwordle" ))
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


#set up of sqlalchemy with database
class Users(db.Model):
    __tablename__ = "user"
    User_id=db.Column("id", db.Integer, primary_key=True)
    name=db.Column("name", db.String(100))
    password=db.Column("password",db.String(100))
    email=db.Column("email",db.String(100))


    def __init__(self, name, password=None, email=None):
        self.password=password
        self.email=email
        self.name=name

class Categories(db.Model):
    __tablename__ = "category"
    category_id=db.Column("id", db.Integer, primary_key=True)
    #word_id_category=db.Column("id", db.Integer, ForeignKey("Words.word_id"))

    def __init__(self, word_id):
        self.word_id=word_id

class Words(db.Model):
    __tablename__="words"
    word_id=db.Column("id", db.Integer, primary_key=True)
    #category_id_words=db.Column("id", db.Integer, ForeignKey("Category.category_id"))
    letter1=db.Column(db.String(1))
    letter2=db.Column(db.String(1))
    letter3=db.Column(db.String(1))
    letter4=db.Column(db.String(1))
    letter5=db.Column(db.String(1))

    def __init__(self, category_id, letter1, letter2, letter3, letter4, letter5):
        self.category_id=category_id
        self.letter1=letter1
        self.letter2=letter2
        self.letter3=letter3
        self.letter4=letter4
        self.letter5=letter5

class UserGames(db.Model):
    __tablename__="user_games"
    game_id=db.Column("id", db.Integer, primary_key=True)
    user_id=Column(Integer,ForeignKey("user.id"))

    def __init__(self, user_id, game_id):
        self.user_id=user_id
        self.game_id=game_id

#for sessions
app.secret_key = "meikftmjei"
#makes session remember name for 5 days
app.permanent_session_lifetime= timedelta(days=5)

@app.route("/login", methods=["POST","GET"])
def login():
    #Post used to send information to the webserver
    if request.method=="POST":
        session.permanent=True
        user=request.form["nm"]
        session["user"]=user
        found_user=Users.query.filter_by(name=user).first()
        Users.query.filter_by(name=user).first()
        if found_user:
            session["email"]=found_user.email
            flash("found user")
        else:
            #adding info to database from session
            usr=Users(user, "")
            db.session.add(usr)
            db.session.commit()


        flash("Login successful", "info")
        return redirect(url_for("user"))
    #else if request method == GET
    else:
        if "user" in session:
            flash("Already logged in", "info")
            return redirect(url_for("user"))
        return render_template("login.html")

# Route for handling the register page logic
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        email=request.form["email"]
        password=request.form["password"]
        found_email=Users.query.filter_by(name=request.args.get("email")).first()
        found_password=Users.query.filter_by(name=request.args.get("password")).first()
        if validated(email, password):
            flash("valid")
            if found_email:
                flash("adding")
                session["email"]=email
                db.session.add(email)
                db.session.add(password)
                db.commit()
                flash("now addded to database","info")
            else:
                flash("email or password already in database")
                return render_template("login.html")
            session["email"]=email
            session["password"]=password
            return render_template("home.html")
        else:
            flash("invalid credentials please include a valid email address and password with numbers and special character")
    return render_template("register.html")

def validated(email, password):
    flash("checking validation")
    regex_email=r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    regex_password=r"\b^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
    if (re.fullmatch(regex_email, email)):
        return True
    else:
        return False
    if (re.fullmatch(regex_password, password)):
        return True
    else:
        return False

@app.route("/user", methods=["POST","GET"])
def user():
    email=None
    if "user" in session:
        #adding user to session
        User_session=session["user"]
        if request.method=="POST":
            email=request.form["email"]
            session["email"]=email
            flash("email was saved")
            #add username to database
            found_user=Users.query.filter_by(name=User_session).first()
            if found_user:
                return render_template ("game.html", title="playgame")
            else:
                flash("No email in database please register", "info")
                return render_template("register.html")
            found_user.email=email
            db.session.commit()

        else:
            if "email" in session:
                email=session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not logged in", "info")
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST","GET"])
def logout():
    #remove user from session
    session.pop("user", None)
    session.pop("email", None)
    flash("You have been logged out", "info")

    return redirect(url_for("login"))


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/leaderboard")
def leaderboard():
    return render_template ("about.html", title="leaderboard")

@app.route("/playgame", methods=["POST","GET"])
def playgame():
    return render_template ("game.html", title="playgame")


if __name__== "__main__":
    db.create_all()
    app.run(port=7383,debug=True)


