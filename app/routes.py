from flask import render_template, session
from markupsafe import escape
from app import app
import get_avito_page

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.cli.command("import-avitodata")
def import_data_from_avito_to_db():
	print("Вызвана функция import-avitodata")
	get_avito_page.get_index_page()
	return "Вызвана функция import-avitodata"

""" 
вызов сервисной страницы отключен временно по согласованию с Собиром,
реализация отложена

@app.route('/service')
def service():
	return render_template('service.html')
"""
