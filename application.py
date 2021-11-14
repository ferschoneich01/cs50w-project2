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
    send(msg, broadcast = True) 


@app.route("/")
@login_required
def index():
    groups = db.execute("SELECT * FROM user_group ug INNER JOIN groups g ON g.id_group = ug.id_group INNER JOIN users u ON ug.id_user = "+session["id_user"]+"").fetchall()    
    friends=[]
    for i,g in groups:
        friends.append([groups[i]["photo"],groups[i]["name"]])

    return render_template("index.html")

@app.route("/create-group", methods=["POST","GET"])
@login_required
def createGroup():
    if request.method == "POST":
        groupName = request.form.get("groupName")
        photo = request.form.get("photo")
        id_user = session["id_user"]
        # Query database for username
        db.execute("INSERT INTO groups (name,photo) VALUES ('"+str(groupName)+"','"+str(photo)+"')")
        db.commit()
        group = db.execute("SELECT * FROM groups WHERE name = '"+groupName+"'").fetchall()
        db.execute("INSERT INTO user_group (id_user,id_group) VALUES ("+id_user+","+group[0]["id_group"]+")")  
        # Redirect user to home page
        return redirect('/')

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
        
        #groups = db.execute("SELECT * FROM user_group ug INNER JOIN groups g ON g.id_group = ug.id_group INNER JOIN users u ON ug.id_user = "+session["id_user"]+"").fetchall()
        
        friends=[]
        #for i,g in groups:
        #friends.append([groups[i]["photo"],groups[i]["name"]])
        friends.append(["data:image/png;base64,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","Community"])
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
