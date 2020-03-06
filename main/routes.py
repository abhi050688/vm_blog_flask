from flask import Blueprint
from flask import render_template,request
from flaskBlog2.models import User, Post


main=Blueprint("main",__name__)

@main.route('/')
@main.route('/home')
def home():
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template('homepage.html',posts=posts)

@main.route('/about')
def aboutpage():
    return render_template('about.html',title='about')
