#!/usr/bin/python3
# coding: utf-8


from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

app = Flask(__name__)
# подгружаем настройки из файла config.py, класс Config
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)

login = LoginManager(app)
# при попытке зайти туда, куда можно только зареганым пользователям вызовется
# url_for(login.login_view)
login.login_view = "login"

mail = Mail(app)

from app import routes, models, errors

import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

if not app.debug:
	if app.config["MAIL_SERVER"]:
		auth = None
		if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
			auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
		secure = None
		if app.config["MAIL_USE_TLS"]:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost = (app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
			fromaddr = "no-reply@" + app.config["MAIL_SERVER"],
			toaddrs = app.config["MAIL_ADDRESSES"], subject = "Microblog failure",
			credentials=auth, secure=secure
			)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)

	if not os.path.exists("logs"):
		os.mkdir("logs")
	file_handler = RotatingFileHandler("logs/microblog.log", maxBytes=10240, backupCount=10)
	file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)

	app.logger.setLevel(logging.INFO)
	app.logger.info("Microblog startup")
