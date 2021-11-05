import os

from flask import Flask, render_template, url_for,request,flash, redirect, session
from flask_socketio import SocketIO, emit,send,leave_room,join_room
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
app.config['SESSION_PERMANENT']= False
Session(app)
socketio = SocketIO(app, manage_session=False)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Recibirá los nuevos mensajes y los emitirá por socket.
@socketio.on('message') # recibir msj del lado del cliente al servidor (EVENTO) . 
def handle_Message(msg): # Comenzamos a manejar el msj.
    #print('Mensaje: ' + msg + 'Username: '+userName) #mensaje en terminal.
    send(msg, broadcast = True) #mensaje al lado del cliente con su transmision.

@socketio.on('left') # recibir msj del lado del cliente al servidor (EVENTO) . 
def left_Message():
    redirect("/") 

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST","GET"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            print('Ingrese un nombre de usuario')
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            print('Ingrese una contraseña')
            return redirect("/login")

        #nomrbre de usuario ingresado
        username = request.form.get("username")
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = '"+username+"'").fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            print('Contraseña Incorrecta')
            return redirect("/login")


        # Remember which user has logged in
        session["id_user"] = rows[0]["id_user"]
        user = db.execute("SELECT * FROM users WHERE username = '"+username+"'").fetchall() 
        username = user[0]["fullname"]
        
        photo = user[0]["image"]
        friends=[]
        friends.append(['https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Noun_Project_Community_icon_986471.svg/1024px-Noun_Project_Community_icon_986471.svg.png','Community Moon Message'])
        # Redirect user to home page
        return render_template("index.html",username=username,photo=photo,friends=friends)
    else:
        return render_template("login.html")

@app.route("/register", methods=["POST","GET"])
def register():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Ingrese un nombre de usuario")
            

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Ingrese una contraseña")

        elif not request.form.get("fullname"):
            flash("Ingrese un fullname")

        elif not request.form.get("email"):
            flash("Ingrese un email")

        elif not request.form.get("sex"):
            flash("Ingrese un sexo")
        
        elif not request.form.get("image"):
            flash("Ingrese una imagen")

        #nomrbre de usuario ingresado
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        sex = request.form.get("select")
        image = request.form.get("image")

        print(username)
        print(password)
        print(fullname)
        print(email)
        print(image)
        
        # Query database for username
        db.execute("INSERT INTO users (username,password,fullname,email,sex,image) VALUES ('"+str(username)+"','"+str(password)+"','"+str(fullname)+"','"+str(email)+"','"+str(sex)+"','"+str(image)+"')")
        db.commit()
        # Redirect user to home page
        
        return redirect("/")
    else:
        return render_template("register.html")
