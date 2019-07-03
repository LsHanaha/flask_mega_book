# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# данные конфига можно задавать либо в файле либо через настройку переменных venv
# export MAIL_PASSWORD=<your-gmail-password>

class Config():
	SECRET_KEY = os.environ.get('SECRET_KEY') or "secret"
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "sqlite:///" + os.path.join(basedir, "app.db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = os.environ.get('MAIL SERVER') or "smtp.googlemail.com"
	MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
	MAIL_USE_TLS = 1
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "kirtrishin"
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or "Stm7935493@@"
	MAIL_ADDRESSES = ["kirtrishin@gmail.com"]
	POSTS_PER_PAGE = 15
	ADMINS=["Me"]
