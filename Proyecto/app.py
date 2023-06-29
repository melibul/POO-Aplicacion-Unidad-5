from datetime import datetime
from flask import Flask, render_template, request, url_for, session, redirect
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

@app.route('/back')
def go_back():
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    else:
        return redirect('/')
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
					return render_template('eleccion.html')
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

			fecha=request.form.get('fecha')
			codigo_clase=request.form.get('clase')
			curso=request.form.get('curso')
			
			return redirect(url_for('guardar_base', fecha=fecha, codigo_clase=codigo_clase, curso=curso))
			
	else:
		cursos = Curso.query.filter_by(idpreceptor=session['idpreceptor']).all()
		return render_template('asistencia.html', cursos = cursos)
@app.route('/guardar_base/<fecha>/<codigo_clase>/<curso>', methods=['GET', 'POST'])
def guardar_base(fecha, codigo_clase, curso):
	estudiantes=Estudiante.query.filter_by(idcurso=curso).order_by(Estudiante.apellido.asc()).all()
	if request.method=='POST':
		justificaciones=request.form.getlist('justificacion[]')
		asistencias=request.form.getlist('asistio[]')
		estudiantes_ids=[estudiante.id for estudiante in estudiantes]
		for  i in range(len(estudiantes_ids)):
			asistencia_nueva=Asistencia()
			asistencia_nueva.fecha=fecha
			asistencia_nueva.codigoclase=codigo_clase
			asistencia_nueva.asistio=asistencias[i] 
			asistencia_nueva.justificacion=justificaciones[i]
			asistencia_nueva.idestudiante=estudiantes_ids[i]
			db.session.add(asistencia_nueva)
			db.session.commit()
		return render_template('eleccion.html')
	else:
		
		return render_template ('lista_estudiantes.html', estudiantes=estudiantes)
@app.route('/informe/', methods=['GET', 'POST'])
def informe():
	if request.method=='POST':
		if not request.form.get('curso'):
			cursos = Curso.query.filter_by(idpreceptor=session['idpreceptor']).all()
			return render_template('seleccion_curso.html', cursos=cursos)
		else:
			curso = Curso.query.filter_by(id=request.form['curso']).first()
			estudiantes=curso.estudiante
			estudiantes=sorted(curso.estudiante, key=lambda estudiante: (estudiante.apellido, estudiante.nombre))
			asistencia_arreglo=[]
			asistencias_lista=Asistencia.query.all()
			i=0
			for c in range(len(estudiantes)):
				asistencia_arreglo.append([0,0,0,0,0,0,0])
			for estudiante in estudiantes:
				for asistencia in asistencias_lista:
					if(estudiante.id==asistencia.idestudiante):
						if(asistencia.codigoclase==1):
							if (asistencia.asistio=='s'):
								asistencia_arreglo[i][0]+=1
							else:
								if(asistencia.justificacion==""):
									asistencia_arreglo[i][2]+=1
								else:
									asistencia_arreglo[i][1]+=1
						else:
							if(asistencia.asistio=='s'):
								asistencia_arreglo[i][3]+=1
							else:
								if(asistencia.justificacion==""):
									asistencia_arreglo[i][5]+=0.5
								else:
									asistencia_arreglo[i][4]+=0.5
						asistencia_arreglo[i][6]=asistencia_arreglo[i][2]+asistencia_arreglo[i][5]+asistencia_arreglo[i][1]+asistencia_arreglo[i][4]
				i+=1
			return render_template('informe.html', estudiantes=estudiantes, asistencia_arreglo=asistencia_arreglo)
	cursos = Curso.query.filter_by(idpreceptor=session['idpreceptor']).all()
	print("ayuda")
	return render_template('seleccion_curso.html', cursos=cursos)
				





if __name__ == '__main__':
		app.run(debug=True)

