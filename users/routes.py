from flask  import Blueprint
from flask import escape, request,render_template,url_for,flash,redirect, Markup, abort
from flaskBlog2.users.forms import LoginForm, RegistrationForm, UpdateForm, RequestResetForm, ResetPasswordForm
from flaskBlog2.models import User, Post
from flaskBlog2 import bcrypt,db
from flask_login import login_user, current_user, logout_user, login_required
from flaskBlog2.users.utils import save_picture, send_reset_email
import secrets
import os

users=Blueprint('users',__name__)


@users.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    forms=LoginForm()
    if forms.validate_on_submit():
        user=User.query.filter_by(email=forms.email.data).first()
        if user and bcrypt.check_password_hash(user.password,forms.password.data):
            login_user(user,remember=forms.remember.data)
            flash(f'Login Successful. Welcome {user.username} !!','success')
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check the email and password.','danger')
    return render_template('login.html',forms=forms)

@users.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    forms=RegistrationForm()
    if forms.validate_on_submit():
        hashed_pwd=bcrypt.generate_password_hash(forms.password.data).decode('utf-8')
        user=User(username=forms.username.data,email=forms.email.data,password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash(f"Account successfully created for {forms.username.data}!",'success')
        return redirect(url_for('users.login'))
    return render_template('register.html',forms=forms)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account',methods=['GET','POST'])
@login_required
def account():
    form=UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash(f'Your account has been updated.','success')
        return redirect(url_for('user.account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file,forms=form)


@users.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with the instruction to reset the password",'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html",title='Reset Password', forms=form)

@users.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash(f'That is an invalid or expired token','warning')
        return redirect(url_for('users.reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pwd=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_pwd
        db.session.commit()
        flash(f"Password reset successful for {user.username}!",'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html",title='Reset Password', forms=form)
