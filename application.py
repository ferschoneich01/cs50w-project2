import os

from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/")
def index():
    friends=[]
    friends.append(['https://www.inboundcycle.com/hubfs/ClaraAlvarez.jpg','Alejandra Torres'])
    friends.append(['https://www.trecebits.com/wp-content/uploads/2019/02/Persona-1-445x445.jpg','Who Lee'])
    return render_template("index.html", friends=friends)

@app.route("/chat")
def chat():
    return render_template("chat.html")
