from flask import render_template, session, flash, redirect, url_for, request, send_from_directory
from markupsafe import escape
from app import app, db
from app.forms import LoginForm, RegistrationForm, NewItem, AddPhoto, ItemListForm
import click
import get_avito_page
from app.models import Item, Image, User, Item_status
from flask_login import logout_user, current_user, login_user, login_required
from datetime import datetime
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os
from PIL import Image as PImage
from config import THUMB_SIZE, img_normal_dir, img_thumb_dir, START_IMG
import time

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
#@login_required Если есть строгое требование работать только с авторизованными пользователями
def index():

    page = request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        if request.method == 'POST':
            current_user.filter_my = int('only_my_ad' in request.form)
            current_user.filter_public = int('unposted_ad' in request.form)
            try:
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                print(err)
            if 'create_new_ad' in request.form:
                return redirect(url_for('additem'))
            elif 'unposted_ad' in request.form:
                i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
                    ((Item.status == 2) | (Item.status == 3)), Item.user_id == current_user.id).group_by(Item).paginate(page, app.config[
                    'ITEMS_PER_PAGE'], False)
            elif 'only_my_ad' in request.form:
                i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
                     Item.user_id == current_user.id).group_by(Item).paginate(page, app.config[
                    'ITEMS_PER_PAGE'], False)
            else:
                i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
                    (Item.status == 1) | (Item.user_id == current_user.id)).group_by(Item).paginate(page, app.config[
                    'ITEMS_PER_PAGE'], False)
        else:
            if current_user.filter_public == 1:
                i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
                    ((Item.status == 2) | (Item.status == 3)), Item.user_id == current_user.id).group_by(Item).paginate(page, app.config[
                    'ITEMS_PER_PAGE'], False)
            elif current_user.filter_my == 1:
                i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
                     Item.user_id == current_user.id).group_by(Item).paginate(page, app.config[
                    'ITEMS_PER_PAGE'], False)
            else:
                i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
                    (Item.status == 1) | (Item.user_id == current_user.id)).group_by(Item).paginate(page, app.config[
                    'ITEMS_PER_PAGE'], False)
    else:
        i_set = db.session.query(Item, Image, Item_status).join(Image).join(Item_status).filter(
            Item.status == 1).group_by(Item).paginate(page, app.config['ITEMS_PER_PAGE'], False)

    next_url = url_for('index', page=i_set.next_num) \
        if i_set.has_next else None
    prev_url = url_for('index', page=i_set.prev_num) \
        if i_set.has_prev else None           
    
    title = "Каталог страница " + str(i_set.page) + " из " + str(i_set.pages)

    if current_user.is_authenticated:
        form = ItemListForm()
        form.only_my_ad.data = bool(current_user.filter_my)
        form.unposted_ad.data = bool(current_user.filter_public)
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            print(err)
#        return redirect(url_for('index', page=current_user.list_page))

        return render_template('item_list.html', title=title, i_list=i_set, next_url=next_url, prev_url=prev_url,
                               form=form, user=current_user.id)
    else:
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

@app.route('/unpublicitem/<ad_num>', methods=['GET', 'POST'])
@login_required
def unpublic_item(ad_num):
    """
    Снятие с публикации
    """
    item_ = Item.query.filter_by(num_of_ad=ad_num, user_id=current_user.id).first_or_404()
    act_stat = Item_status.query.filter_by(description='active').first().key
    edit_stat = Item_status.query.filter_by(description='on_edit').first().key
    if item_.status == act_stat:
        item_.status = edit_stat
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
    return redirect(url_for('index'))

@app.route('/deleteitem/<ad_num>', methods=['GET', 'POST'])
@login_required
def delete_item(ad_num):
    """
    Пометка объекта в базе, как удаленный
    """
    item_ = Item.query.filter_by(num_of_ad=ad_num, user_id=current_user.id).first_or_404()
    edit_stat = Item_status.query.filter_by(description='on_edit').first().key
    deleted_stat = Item_status.query.filter_by(description='deleted').first().key
    if item_.status == edit_stat:
        item_.status = deleted_stat
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
    return redirect(url_for('index'))


@app.route('/deletepitem/<ad_num>', methods=['GET', 'POST'])
@login_required
def delete_item_permanent(ad_num):
    """
    Перманентное удаление объявления
    Удаление фото с диска, записей о фото из базы, объявление
    """
    item_ = Item.query.filter_by(num_of_ad=ad_num, user_id=current_user.id).first_or_404()
    deleted_stat = Item_status.query.filter_by(description='deleted').first().key
    if item_.status == deleted_stat:
        #Удаляем картинки с диска
        images_db = db.session.query(Image).filter(Image.num_of_ad == ad_num).all()
        images_ = [[str(ind), image.image_path] for ind, image in enumerate(images_db)]

        if images_ != []:
            for image in images_:
                fo_norm = os.path.join(img_normal_dir, image[1])
                fo_thumb = os.path.join(img_thumb_dir, image[1])
                if image[1] != START_IMG:
                    try:
                        os.remove(fo_norm)
                        os.remove(fo_thumb)
                    except Exception as err:
                        print(err)
            #Удаляем картинки из базы, удаляем объявление из базы
            try:
                db.session.query(Image).filter(Image.num_of_ad == ad_num).delete()
                db.session.flush()
                db.session.delete(item_)
                db.session.commit()
            except:
                db.session.rollback()

    return redirect(url_for('index'))


@app.route('/edititem/<ad_num>', methods=['GET', 'POST'])
@login_required
def edit_item(ad_num):


    item_ = Item.query.filter_by(num_of_ad=ad_num, user_id=current_user.id).first_or_404()
    edit_stat = Item_status.query.filter_by(description='on_edit').first()
    if item_.status != edit_stat:
        item_.status = edit_stat
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
    title = "Объявление " + item_.num_of_ad

    if request.method == 'GET':

        images_ = db.session.query(Image).filter(Image.num_of_ad == ad_num).all()
        images_ = [[str(ind), image.image_path] for ind, image in enumerate(images_)]

        if item_:
            images_ = db.session.query(Image).filter(Image.num_of_ad == ad_num).all()
            images_to_render = [[str(ind), image.image_path] for ind, image in enumerate(images_)]

            form_img = AddPhoto()

            form = NewItem(formdata=request.form, obj=item_)

            images_ = db.session.query(Image).filter(Image.num_of_ad == ad_num).all()
            images_ = [[str(ind), image.image_path] for ind, image in enumerate(images_)]

            return render_template('edititem.html', title=title, form=form, form_img=form_img, images=images_)
        else:
            return 'Error loading #{ad_num}'.format(id=ad_num)
    else:

        if "add_photo" in request.form:

            images_db = db.session.query(Image).filter(Image.num_of_ad == ad_num).all()
            images_ = [[str(ind), image.image_path] for ind, image in enumerate(images_db)]

            if images_ != []:
                for image in images_:
                    fo_norm = os.path.join(img_normal_dir, image[1])
                    fo_thumb = os.path.join(img_thumb_dir, image[1])
                    if image[1] != START_IMG:
                        try:
                            os.remove(fo_norm)
                            os.remove(fo_thumb)
                        except Exception as err:
                            print(err)
                try:
                    db.session.query(Image).filter(Image.num_of_ad == ad_num).delete()
                    db.session.commit()
                except:
                    db.session.rollback()

            form_img = AddPhoto()
            images_ = []
            for ind, file in enumerate(form_img.images_.data):
                mills = int(time.time()%1*100000)
                fo_name = ad_num + "_" + (f"{str(mills):>5}").replace(" ", "0") + "_" + (f"{str(ind):>3}").replace(" ", "0") + ".jpg"
                fo_norm = os.path.join(img_normal_dir, fo_name)
                fo_thumb = os.path.join(img_thumb_dir, fo_name)

                # file_filename = secure_filename(file.filename)
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

                image_to_db = Image(num_of_ad=ad_num, image_path=fo_name)
                try:
                    db.session.add(image_to_db)
                except Exception as err:
                    print(err)
                    db.session.rollback()
                images_.append(fo_name)
            try:
                db.session.commit()
            except Exception as err:
                print(err)
                db.session.rollback()
            images_ = [[str(ind), image] for ind, image in enumerate(images_)]

            item_ = Item.query.filter_by(num_of_ad=ad_num, user_id=current_user.id).first_or_404()
            form = NewItem(formdata=request.form, obj=item_)
            #images_ = db.session.query(Image).filter(Image.num_of_ad == ad_num).all()
            #images_ = [[str(ind), image.image_path] for ind, image in enumerate(images_)]
            return render_template('edititem.html', title=title, form=form, form_img=form_img, images=images_)

        elif "set_aside" in request.form:

            item_.description = request.form['description']
            item_.price = request.form['price']
            item_.address = request.form['address']
            item_.extended_text = request.form['extended_text']
            try:
                db.session.commit()
            except Exception as err:
                db.session.rollback()
            return redirect(url_for('index'))


        elif "submit" in request.form:

            item_.description = request.form['description']
            item_.price = request.form['price']
            item_.address = request.form['address']
            item_.extended_text = request.form['extended_text']
            item_.status = Item_status.query.filter_by(description='active').first().key
            try:
                db.session.commit()
            except Exception as err:
                db.session.rollback()

            return redirect(url_for('index'))




@app.route('/additem', methods=['GET', 'POST'])
@login_required
def additem():


    i_status = Item_status.query.filter_by(description='on_edit').first()
    ad_on_edit = Item.query.filter_by(user_id=current_user.id, status=i_status.key).count()
    
    if ad_on_edit < 5:
        new_item = Item(num_of_ad='000000000', creation_date=datetime.now(), user_id=current_user.id, status=i_status.key)



        db.session.add(new_item)
        db.session.flush()

        new_num_of_ad = 'L' + str(new_item.key)
        new_item.num_of_ad = new_num_of_ad
        def_image = Image(num_of_ad=new_num_of_ad, image_path=START_IMG)
        db.session.add(def_image)
        try:
            db.session.commit()
        except Exception as err:
            print(err)

        redirect_url = '/edititem/'  + new_num_of_ad
        return redirect(redirect_url)
    else:
        flash("У вас много незаконченных объявлений")
        return redirect(url_for('index'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')

