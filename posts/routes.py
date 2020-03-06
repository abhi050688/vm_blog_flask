from flask import Blueprint
from flask import escape, request,render_template,url_for,flash,redirect, Markup, abort
from flaskBlog2.users.forms import LoginForm, RegistrationForm, UpdateForm, RequestResetForm, ResetPasswordForm
from flaskBlog2.posts.forms import PostForm, UpdatePostForm
from flaskBlog2.models import User, Post
from flaskBlog2 import bcrypt,db,mail
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os

posts=Blueprint("posts",__name__)


@posts.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
    forms=PostForm()
    if forms.validate_on_submit():
        post=Post(title=forms.title.data,content=Markup(forms.content.data),author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f"Your post has been created",'success')
        return redirect(url_for('main.home'))
    return render_template("create_post.html",forms=forms, type="Create")


@posts.route('/post/<int:post_id>')
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template("post.html",post=post)

@posts.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if current_user==post.author:
        forms=UpdatePostForm()
        if forms.validate_on_submit():
            post.title=forms.title.data
            post.content=forms.content.data
            db.session.commit()
            flash(f"Your post has been updated!",'success')
            return redirect(url_for('posts.post',post_id=post.id))
        elif request.method=='GET':
            forms.title.data=post.title
            forms.content.data=post.content
        return render_template("create_post.html",forms=forms, type="Update")
    else:
        abort(403)

@posts.route('/post/<int:post_id>/delete',methods=['POST'])
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(f"Your post has been deleted!",'danger')
    return redirect(url_for('main.home'))
