import os
import shutil
import csv
import sys
import os
import sqlite3
""" from flask_sqlalchemy import SQLAlchemy """
from flask import Flask,render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_bootstrap import Bootstrap
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

app = Flask(__name__)
port = int(os.getenv("PORT", 8000))

bootstrap = Bootstrap(app)


	 
# DATABASE
connection = sqlite3.connect('people.db', check_same_thread=False)
conn = sqlite3.connect('classes.db', check_same_thread=False)
print("Opened Database Successfully")

# Configurations
app.config['SECRET_KEY'] = '123456'


# ROUTES!

# HOME
@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html', result={})

# HELP
@app.route('/help')
def help():
	text_list = []
	# Python Version
	text_list.append({
		'label':'Python Version',
		'value':str(sys.version)})
	# os.path.abspath(os.path.dirname(__file__))
	text_list.append({
		'label':'os.path.abspath(os.path.dirname(__file__))',
		'value':str(os.path.abspath(os.path.dirname(__file__)))
		})
	# OS Current Working Directory
	text_list.append({
		'label':'OS CWD',
		'value':str(os.getcwd())})
	# OS CWD Contents
	label = 'OS CWD Contents'
	value = ''
	text_list.append({
		'label':label,
		'value':value})
	return render_template('help.html',text_list=text_list,title='help')


# DELETE
@app.route('/delete', methods=["GET"])
def delete_by_name():
	ret = []
	cur = conn.cursor()
	cur.execute('SELECT * FROM people where Name is Not Null')
	result = cur.fetchall()
	return render_template('delete.html', result=result)	

@app.route('/delete', methods=["POST"])
def delete():
	name = request.form.get('opt')
	cur = conn.cursor()
	if name != '':
		cur.execute('DELETE FROM people WHERE Name = (?)', ( name, ))
	conn.commit()
	return redirect(url_for("just_hello2"))	

@app.route('/list2', methods=["GET"])
def just_hello2():
	cur = conn.cursor()
	sql = "SELECT * FROM people where Name is Not Null;"
	cur.execute(sql)
	result = cur.fetchall()
	return render_template('delete.html', result=result)


# INSERT
@app.route('/insert', methods=["GET"])
def insert_by_room():
	cur = conn.cursor()
	cur.execute('SELECT * FROM  classes')
	result = cur.fetchall()
	return render_template('insert.html', result=result)


@app.route('/insert', methods=["POST"])
def insert():
	if request.method == 'POST':
		Name = request.form['Name']
		State = request.form['State']
		Salary = request.form['Salary']
		Grade = request.form['Grade']
		Room = request.form['Room']
		Telnum = request.form['Telnum']
		Picture = request.form['Picture']
		Keywords = request.form['Keywords']
	cur = connection.cursor()
	cur.execute('INSERT INTO people VALUES(?,?,?,?,?,?,?,?)', (Name, State, Salary, Grade, Room, Telnum, Picture, Keywords))
	conn.commit()
	return redirect(url_for("just_hello1"))

@app.route('/list1', methods=["GET"])
def just_hello1():
	cur = conn.cursor()
	sql = "SELECT * FROM classes where max is Not Null;"
	cur.execute(sql)
	result = cur.fetchall()
	return render_template('insert.html', result=result)


# NAME SEARCH
@app.route('/search_name', methods=["GET"])
def search_by_name():
	ret = []
	return render_template('name_search.html', result=ret)

@app.route('/search_name', methods=["POST"])
def search_name():
	name = request.form["name"]
	cur = connection.cursor()
	cur.execute('SELECT * FROM people WHERE Name = (?)', (name, ))
	result = cur.fetchall()
	return render_template('name_search.html', result=result)	


# SEARCH KEYWORD

@app.route('/search_sal', methods=["GET"])
def search_sal():
	ret = []
	return render_template('salary_search.html', result=ret)

@app.route('/search_sal', methods=["POST"])
def search_by_sal():
	sal_st = request.form["sal_start"]
	sal_end = request.form["sal_end"]
	if sal_st == '' and sal_end == '':
		sal_st = 0
		sal_end = 0
	if sal_st == '':
		sal_st = 0
	if sal_end == '':
		sal_end = 0
	cur = conn.cursor()
	cur.execute('SELECT * FROM people WHERE Salary between (?) and (?) ', (sal_st, sal_end, ))
	result = cur.fetchall()
	return render_template('salary_search.html', result=result)


# UPDATE
@app.route('/update', methods=["GET"])
def update_by_room():
	cur = conn.cursor()
	cur.execute('SELECT * FROM classes where max is Not Null')
	result = cur.fetchall()
	return render_template('update.html', result=result)


@app.route('/update', methods=["POST"])
def update():
	name = request.form.get('opt')
	caption = request.form["caption"]
	salary = request.form["salary"]
	cur = conn.cursor()
	if  caption != '':
		cur.execute('UPDATE people SET Keywords = (?), Salary = (?) WHERE Name = (?)', (caption, salary, name,))
	conn.commit()
	return redirect(url_for("just_hello"))	


@app.route('/list', methods=[ "GET"])
def just_hello():
	cur = conn.cursor()
	sql = "SELECT * FROM people where Name is Not Null;"
	cur.execute(sql)
	result = cur.fetchall()
	return render_template('update.html', result=result)


# UPLOAD
UPLOAD_FOLDER = '.../static/pics'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route('/upload', methods = ["GET","POST"])	
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('upload.html')
			
@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
	return render_template('404.html',title='404')

@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
	return render_template('500.html',title='500')


# if __name__ == '__main__':
# 	app.run(host='0.0.0.0', port=port)