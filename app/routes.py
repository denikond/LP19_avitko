from flask import render_template, session
from markupsafe import escape
from app import app, db
import click
import get_avito_page
from app.models import Item, Image


@app.route('/')
@app.route('/index')
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


""" 
вызов сервисной страницы отключен временно по согласованию с Собиром,
реализация отложена

@app.route('/service')
def service():
	return render_template('service.html')
"""
