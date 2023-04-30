import os
import time
import datetime
from flask import Flask, render_template, url_for, request, flash, redirect, session, make_response
from flask_socketio import SocketIO, emit, send, leave_room, join_room
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from funciones import *
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY is not set")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or 'Secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
Session(app)
socketio = SocketIO(app, manage_session=False)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Recibirá los nuevos mensajes y los emitirá por socket.


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""
    print(data['username'])
    msg = data["msg"]
    session["username"] = data['username']
    room = data["room"]
    # Set timestamp
    time_stamp = time.strftime('%b-%d %I:%M%p', time.localtime())
    emit("incoming-msg", {"username": username, "msg": msg,
         "time_stamp": time_stamp, "room": room}, room=room)


@socketio.on('join')
def on_join(data):
    username = data['username']
    session["username"] = data['username']
    room = data['room']
    join_room(room)
    emit("incoming-log-join", username + ' esta en linea.', to=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    session["username"] = data['username']
    room = data['room']
    leave_room(room)
    emit("incoming-log-leave", username + ' esta desconectado.', to=room)


@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT * FROM users WHERE id_user = " +
                      str(session["id_user"])+"").fetchall()
    groups = db.execute("SELECT * FROM user_group ug INNER JOIN public.group g ON g.id_group = ug.id_group AND ug.id_user = " +
                        str(session["id_user"])+"").fetchall()
    friends = []
    username = rows[0]["username"]
    photo = rows[0]["image"]
    session["username"] = username
    i = 0
    for g in groups:
        friends.append([groups[i]["photo"], groups[i]["name"]])
        i = i+1
    res = make_response(render_template(
        "index.html", friends=friends, username=username, photo=photo))

    if 'samesite' in session and session['samesite'] is None:

        cookie = "{}; {}".format(cookie, b'SameSite=None'.decode('latin1'))
        print(cookie)
        res.headers.add(
            'Set-Cookie',
            cookie
        )
    return res


@app.route("/join-group", methods=["POST", "GET"])
@login_required
def joingroup():
    if request.method == "POST":
        group = request.form.get("searchgroup")
        print(group)
        rows = db.execute(
            "SELECT * FROM public.group WHERE name = '"+group+"'").fetchall()
        db.execute("INSERT INTO user_group (id_user,id_group) VALUES (" +
                   str(session["id_user"])+","+str(rows[0]["id_group"])+")")
        db.commit()
        return redirect("/")


@app.route("/create-group", methods=["POST", "GET"])
@login_required
def createGroup():
    if request.method == "POST":
        if not request.form.get("groupName"):
            flash("Ingrese el nombre de un grupo")

        if not request.form.get("photo"):
            flash("Seleccione una foto")
        else:
            groupName = request.form.get("groupName")
            photo_group = request.form.get("photo")
            id_user = session["id_user"]
            # Query database for username
            db.execute("INSERT INTO public.group (name,photo) VALUES ('" +
                       str(groupName)+"','"+str(photo_group)+"')")
            db.commit()
            group = db.execute(
                "SELECT * FROM public.group WHERE name = '"+str(groupName)+"'").fetchall()
            db.execute("INSERT INTO user_group (id_user,id_group) VALUES (" +
                       str(id_user)+","+str(group[0]["id_group"])+")")
            db.commit()
            # Redirect user to home page

    return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    # Forget any user_id
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("ingrese un nombre de usuario")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("ingrese un nombre de usuario")
            return redirect("/login")

        # nomrbre de usuario ingresado
        username = request.form.get("username")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = '"+username+"'").fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            print('Contraseña Incorrecta')
            return redirect("/login")

        # Remember which user has logged in
        session["id_user"] = rows[0]["id_user"]
        session["username"] = username

        # Redirect user to home page
        return redirect("/")
    else:
        res = make_response(render_template("login.html"))
        if 'samesite' in session and session['samesite'] is None:
            cookie = "{}; {}".format(cookie, b'SameSite=None'.decode('latin1'))

            res.headers.add(
                'Set-Cookie',
                cookie
            )
        return res


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Ingrese un nombre de usuario')
            return redirect('/register')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Ingrese una contraseña')
            return redirect("/register")

        elif not request.form.get("fullname"):
            flash('Ingrese un fullname')
            return redirect("/register")

        elif not request.form.get("email"):
            flash('Ingrese un email')
            return redirect("/register")

        elif not request.form.get("sex"):
            flash('Ingrese un sexo')
            return redirect("/register")

        elif not request.form.get("image"):
            flash('Ingrese una imagen')
            return redirect("/register")

        # nomrbre de usuario ingresado
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        sex = request.form.get("sex")
        image = request.form.get("image")
        # print(username+"-"+password+"-"+fullname+"-"+email+"-"+sex+"-"+image)
        # Query database for username
        db.execute("INSERT INTO users (username,password,fullname,email,sex,image) VALUES ('"+str(username) +
                   "','"+str(password)+"','"+str(fullname)+"','"+str(email)+"','"+str(sex)+"','"+str(image)+"')")
        db.commit()
        # Redirect user to home page

        return redirect("/")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
