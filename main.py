import requests
import random
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from data import db_session
from forms.user import RegisterForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"


def get_latest_news(channel_name, n):
    telegram_url = "https://t.me/s/"
    channel_url = telegram_url + channel_name
    response = requests.get(channel_url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    url = links[-1]["href"]
    url = url.replace(telegram_url, "")
    news_id = int(url.split("/")[-1])
    urls = []
    for i in range(n):
        urls.append(f"{channel_name}/{news_id - i}")
    return urls


@app.route("/", methods=["GET", "POST"])
def index():
    popular_channels = ["melfm", "habr_com", "rian_ru", "vysokygovorit"]
    urls = get_latest_news(random.choice(popular_channels), 5)  # добавить самые популярные новости для конкретного пользователя
    if request.method == "GET":
        return render_template("index.html", urls=urls)
    else:
        channel_name = request.form["adress"]
        news_amount = int(request.form["newsAmount"])
        theme = request.form["theme"]
        urls = get_latest_news(channel_name, news_amount)
        return render_template("index.html", urls=urls, theme=theme)


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("base.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template("register.html", title="Регистрация", form=form)


if __name__ == "__main__":
    db_session.global_init("db/database.db")
    app.run()
