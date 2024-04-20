import requests
import random
from flask import Flask, render_template, request, redirect, session
from bs4 import BeautifulSoup
from data import db_session
from data.users import User
from forms.editform import EditForm
from forms.loginform import LoginForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def get_latest_news(channel_name, n):
    telegram_url = "https://t.me/s/"
    channel_url = telegram_url + channel_name
    try:
        response = requests.get(channel_url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")
        url = links[-1]["href"]
        url = url.replace(telegram_url, "")
        news_id = int(url.split("/")[-1])
    except Exception as e:
        return []
    else:
        urls = []
        for i in range(n):
            urls.append(f"{channel_name}/{news_id - i}")
        return urls


@app.route("/", methods=["GET", "POST"])
def index():
    if not current_user.is_authenticated:
        popular_channels = ["melfm", "habr_com", "rian_ru", "vysokygovorit"]
        urls = get_latest_news(random.choice(popular_channels), 5)
        if request.method == "GET":
            return render_template("index.html", urls=urls)
        else:
            channel_name = request.form["adress"]
            news_amount = int(request.form["newsAmount"])
            theme = request.form["theme"]
            urls = get_latest_news(channel_name, news_amount)
            return render_template("index.html", urls=urls, theme=theme)
    else:

        user_id = session.get("_user_id")
        db_sess = db_session.create_session()
        user_channels: list = db_sess.query(User).filter(User.id == user_id).first().channels.split(" ")

        if request.method == "GET":
            urls = get_latest_news(random.choice(user_channels), 5)
            return render_template("index.html", urls=urls, channels=user_channels)
        else:
            channel_name = request.form["adress"]
            news_amount = int(request.form["newsAmount"])
            theme = request.form["theme"]
            urls = get_latest_news(channel_name, news_amount)
            return render_template("index.html", urls=urls, theme=theme, channels=user_channels)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            channels=form.channels.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template("register.html", title="Регистрация", form=form)


@app.route('/profile', methods=["GET", "POST"])
def profile():
    form = EditForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == session.get("_user_id")).first()
        user.name = form.name.data
        user.channels = form.channels.data
        db_sess.commit()
        return redirect("/profile")
    return render_template("profile.html", title="Профиль", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init("db/database.db")
    app.run()
