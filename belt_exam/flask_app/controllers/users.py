from flask import render_template, request, redirect, session, flash
from flask_app import app, Bcrypt
from flask_app.models.user import User
from flask_app.models.magazine import Magazine
import re

bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    print(request.form)
    if User.get_by_email(request.form):
        flash('Email already registered')
        return redirect('/')
    if not User.validate_user(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password" : pw_hash
    }
    user_id = User.save(data)
    session['user_id'] = user_id
    session['user_name'] = data['first_name']
    return redirect('/dashboard')

@app.route('/dashboard')                      
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('dashboard.html', magazines=Magazine.get_all())

@app.route('/login', methods=['POST'])
def login():
    data = { "email" : request.form["email"] }
    user_in_db = User.get_by_email(data)
    print(data)
    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password")
        return redirect('/')
    session['user_id'] = user_in_db.id
    session['user_name'] = user_in_db.first_name
    return redirect("/dashboard")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('new_magazine.html')

@app.route('/create_m', methods=['POST'])
def create_m():
    if not Magazine.validate_magazine(request.form):
        return redirect('/create')
    id = Magazine.save(request.form)
    return redirect('/dashboard')

@app.route('/show_mag/<int:id>')
def show_mag(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {"id":id}
    return render_template('show_magazine.html',magazine=Magazine.get_one(data))

@app.route('/update/<int:id>')
def update(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {"id":id}
    return render_template('edit_magazines.html', user=User.get_user_with_magazines(data))

@app.route('/update_user',methods=['POST'])
def update_user():
    data = {"id":id}
    session['user_name'] = request.form['first_name']
    User.update(request.form)
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    data = {"id":id}
    Magazine.destroy(data)
    return redirect('/dashboard')