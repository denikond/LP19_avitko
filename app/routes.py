from flask import render_template, session, flash, redirect, url_for, request
from markupsafe import escape
from app import app, db
from app.forms import LoginForm, RegistrationForm
import click
import get_avito_page
from app.models import Item, Image, User
from flask_login import logout_user, current_user, login_user, login_required
from datetime import datetime
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
#@login_required Если есть строгое требование работать только с авторизованными пользователями
def index():
    title = "Объявления по теме"
    #i_set = Item.query.limit(20).offset(1).all()
    i_set = db.session.query(Item,Image).join(Image).group_by(Item).limit(20).all()
    
    #iset = ['One','Two','Three']
    
    #return render_template('item_list.html', page_title=title, ilist=iset)
    return render_template('item_list.html', page_title=title, i_list=i_set)

@app.cli.command("import-avitodata")
@click.argument('start_index_page', nargs=1)
@click.argument('stop_index_page', nargs=1)
def import_data_from_avito_to_db(start_index_page, stop_index_page):
    """ 
    Функция import-avitodata предназначена для импорта данных с avito
    вызывается с аттрибутами начальная и конечная индексная страница
    
    Примеры: 
     
        flask import-avitodata 1 20
        Импортирует объявления попавшие с 1 по 20 индексные страницы
        
        flask import-avitodata 5 5
        Импортирует объявления попавшие на 5й индексной странице
        
    """
    print("Вызвана функция import-avitodata с аттрибутами", start_index_page, stop_index_page)
    if stop_index_page >= start_index_page:
        get_avito_page.get_index_page(pagenum_start=int(start_index_page), pagenum_end=int(stop_index_page))
    else:
        print('Начальная страница сканирования должна быть больше или равна конечной')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(creation_date=datetime.now(), username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

"""
вызов сервисной страницы отключен временно по согласованию с Собиром,
реализация отложена

@app.route('/service')
def service():
    return render_template('service.html')
"""
