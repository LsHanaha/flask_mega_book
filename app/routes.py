# coding: utf-8

from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
# как реализована функция current_user?
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from flask_babel import _


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))
    page = request.args.get('page', 1, type=int)
    posts = (current_user.followed_posts()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


# If the user navigates to /index, for example, the @login_required decorator
# will intercept the request and respond with a redirect to /login,
# but it will add a query string argument to this URL, making the complete
# redirect URL /login?next=/index


@app.route('/login', methods=['POST', 'GET'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    # выполняет проверку формы при входе на страницу и рэндерит форму логина - Get.
    # Если кнопка была нажата инициируется запрос типа POST, если все поля заполнены верно то
    # вернется True, в противном случае False
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("login"))
        # Добавляем юзера в список залогиненых.
        login_user(user, remember=form.remember_me.data)
        # фласк парсит url и смотрит есть ли в переданных параметрах переменная next
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        flash(_("next_page = {}".format(next_page)))
        return redirect(next_page)
    return render_template('login.html', title="sign In", form=form)

@app.route('/register', methods=['POST', 'GET'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congrats, you are user now!"))
        return redirect(url_for('login'))
    return render_template("regitster.html", title="Registration", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>', methods=['POST', 'GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config["POSTS_PER_PAGE"], False)
    next_url = url_for("user", username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for("user", username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template("user.html", user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if form.username.data:
            current_user.username = form.username.data
        if form.about_me.data:
            current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes saved!"))
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User {} not found.'.format(username)))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following {}!'.format(username)))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User {} not found.'.format(username)))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following {}.'.format(username)))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for("explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("explore", page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home',
                           posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_("Check your email for instructions to reset password"))
        return redirect(url_for("login"))
    return render_template("reset_password_request.html", title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        flash(_("Wrong change passwod link"))
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Password reset"))
        return redirect(url_for("login"))
    return render_template("reset_password.html", form=form)
