from flask import render_template, session, flash, redirect, url_for, request, send_from_directory
from markupsafe import escape
from app import app, db
from app.forms import LoginForm, RegistrationForm, NewItem, AddPhoto
import click
import get_avito_page
from app.models import Item, Image, User
from flask_login import logout_user, current_user, login_user, login_required
from datetime import datetime
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os
from PIL import Image as PImage
from config import THUMB_SIZE

@app.route('/')
@app.route('/index')
#@login_required Если есть строгое требование работать только с авторизованными пользователями
def index():
        
    page = request.args.get('page', 1, type=int)
    i_set = db.session.query(Item,Image).join(Image).group_by(Item).paginate(page, app.config['ITEMS_PER_PAGE'], False)

    next_url = url_for('index', page=i_set.next_num) \
        if i_set.has_next else None
    prev_url = url_for('index', page=i_set.prev_num) \
        if i_set.has_prev else None           
    
    title = "Каталог страница " + str(i_set.page) + " из " + str(i_set.pages)

    return render_template('item_list.html', title=title, i_list=i_set, next_url=next_url, prev_url=prev_url)


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

@app.route('/item/<ad_num>')
def my_item(ad_num):

    item_ = Item.query.filter_by(num_of_ad=ad_num).first_or_404()
    title = "Объявление " + item_.num_of_ad

    images_ = db.session.query(Image).filter(Image.num_of_ad==ad_num).all()
    images_ = [[str(ind), image.image_path] for ind, image in enumerate(images_)]
    
    return render_template('item.html', title=title, item_=item_, images=images_)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
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
        flash('Поздравляю, теперь Вы - зарегистрированый пользователь')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/additem', methods=['GET', 'POST'])
@login_required
def additem():
    
    images_ = []
    form = NewItem()
    form_img = AddPhoto()
    

    if form.validate_on_submit():


        item_ = Item(description=form.description.data, num_of_ad='000000000', creation_date=datetime.now(), \
            address=form.address.data, price=form.price.data, extended_text=form.extended_text.data,user_id=current_user.id)
        
        db.session.add(item_)
        db.session.flush()

        item_.num_of_ad = 'L' + str(item_.key)

        db.session.commit()
        flash('Создано новое объявление')
        return redirect(url_for('index'))

    elif form_img.validate_on_submit():
        images_ = []
        for ind, file in enumerate(form_img.images_.data):

            fo_name = str(current_user.id) + "_" + (f"{str(ind):>3}").replace(" ","0") + ".jpg"
            fo_norm = os.path.join(app.config['TEMP_FOLDER'], 'normal', fo_name)
            fo_thumb = os.path.join(app.config['TEMP_FOLDER'], 'thumb', fo_name)

            #file_filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(fo_norm))
            except Exception as err:
                print(err)
            else:
                try:
                    with PImage.open(fo_norm) as im:
                        im.thumbnail(THUMB_SIZE)
                        im.save(fo_thumb, "JPEG")
                except OSError:
                    flash("Не возможно создать миниатюру для ", fo_norm)
                else:
                    flash("Создана миниатюра ", fo_thumb)

            images_.append(fo_name)

        images_ = [[str(ind), image] for ind, image in enumerate(images_)]

        return render_template('additem.html', title='Новое объявление', form=form, form_img=form_img, images=images_, cache='no_cache')




    return render_template('additem.html', title='Новое объявление', form=form, form_img=form_img, images=images_, cache='no_cache')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')

"""
вызов сервисной страницы отключен временно по согласованию с Собиром,
реализация отложена

@app.route('/service')
def service():
    return render_template('service.html')
"""
