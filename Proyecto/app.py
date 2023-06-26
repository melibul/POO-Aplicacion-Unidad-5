from datetime import datetime
from flask import Flask, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import hashlib
import hmac
app=Flask(__name__)
app.config.from_pyfile('config.py')
app.config['TEMPLATES_AUTO_RELOAD'] = True

from models import db
from models import Preceptor, Curso, Estudiante, Asistencia

@app.route('/')
def sesion():
	return render_template('sesion.html')
@app.route('/ingreso/', methods=['GET','POST'])
def ingreso():
	if request.method =='POST':
		if not request.form.get('correo') or not request.form.get('clave') or not request.form.get('tipo_usuario'):
			return render_template('error.html', error="Faltan datos. Complete toda la información")
		else:
			preceptor_actual= Preceptor.query.filter_by(correo= request.form.get('correo')).first()
			if preceptor_actual is None:
				return render_template('error.html', error="El correo no está registrado")
			else:
				clave = request.form.get('clave').encode('utf-8')
				hashed_password = hashlib.md5(clave).hexdigest()
				verificacion = hmac.compare_digest(hashed_password, preceptor_actual.clave)
				if (verificacion):
					session['idpreceptor']=preceptor_actual.id                    
					return render_template('eleccion.html', usuario = preceptor_actual)
				else:
					return render_template('error.html', error="La contraseña no es válida")
	else:
		return render_template('ingreso.html')
@app.route('/eleccion/', methods=['POST'])
def eleccion():
	if request.method=='POST':
		return render_template('eleccion.html')
	return render_template('eleccion.html') 
@app.route('/asistencia/', methods=['GET','POST'])
def asistencia():
	if request.method=='POST':
		if not request.form.get('curso'):
			cursos = Curso.query.filter_by(idpreceptor=session['idpreceptor']).all()
			return render_template('asistencia.html', cursos = cursos)
		else:
			fecha = request.form['fecha']
			codigo_clase = request.form['clase']
			curso_seleccionado = request.form['curso']
			return render_template('lista_estudiantes.html',fecha = fecha,codigo_clase = codigo_clase,curso_seleccionado = curso_seleccionado)            
	else:
		cursos = Curso.query.filter_by(idpreceptor=session['idpreceptor']).all()
		return render_template('asistencia.html', cursos = cursos)
			
if __name__ == '__main__':
	app.run(debug=True)

