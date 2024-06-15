from flask import Flask,request
from blogapp.models import db, User

admin_db = Blueprint('admin',__name__,url_prefix='/admin')

@app.route("/",method=['POST'])
def root():
    name = request.form['name']
    password = request.form['password']
    new = User(email = name,password=password)
    db.session.add(new)
    db.session.commit()
    return "hi xx"