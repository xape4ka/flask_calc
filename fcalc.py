#!flask/bin/python

from __future__ import absolute_import
from flask import Flask, request, render_template, redirect, url_for, jsonify
from celery import Celery
from celery.utils.log import get_task_logger
from flask_sqlalchemy import SQLAlchemy
import json
import time
from celery import uuid
import ast
from sqlalchemy import text
 
logger = get_task_logger(__name__)
fcalc = Flask(__name__)
fcalc.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
fcalc.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672//'
fcalc.config['CELERY_RESULT_BACKEND'] = 'amqp'
fcalc.config['CELERY_TASK_SERIALIZER'] = 'json'
fcalc.config['CELERY_RESULT_SERIALIZER'] = 'json'

celery = Celery(fcalc, backend="amqp")
db = SQLAlchemy(fcalc)
 
class Log(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    ip = db.Column('ip', db.String(50))
    date = db.Column('date', db.String(255))
    arguments = db.Column('arguments', db.String(255))
    action = db.Column('action', db.String(255))
    result = db.Column('result', db.String(255))

@fcalc.route('/history', methods=['GET'])
def history():
    dt = str(time.time() - 86400)
    countP = db.session.query(Log).filter_by(action='plus').filter(text("date>=%s" % dt)).count()
    countD = db.session.query(Log).filter_by(action='div').filter(text("date>=%s" % dt)).count()
    countM = db.session.query(Log).filter_by(action='mult').filter(text("date>=%s" % dt)).count()
    countM2 = db.session.query(Log).filter_by(action='mult2').filter(text("date>=%s" % dt)).count()
    history = {'Сложение' : countP, 'Умножение' : countM, 'Деление' : countD, 'Возведение в степень' : countM2}
    return json.dumps(history)

@fcalc.route('/', methods=['GET', 'POST'])
def calc():
    if request.method == 'GET':
        return render_template('calc.html')
    a = request.form['a']
    b = request.form['b']
    act = request.form['act']
    if request.form['submit'] == 'Calc':
        json_str = json.dumps({'act': act, 'a': a, 'b': b})
        result = test.delay(json_str)
        while not result.ready():
            pass
        json_data = ast.literal_eval(result.result)
        l = Log(ip = str(request.remote_addr), date=str(time.time()), arguments=json_str, action=act, result=json_data['value'])
        db.session.add(l)
        db.session.commit()
        return(result.result)
    return redirect(url_for('calc'))
 
@celery.task(name='fcalc.test')
def test(json_str):
    expr = json.loads(json_str)
    if expr['act'] == 'plus':
        c = int(expr['a']) + int(expr['b'])
        aa = {"value": c}
        return (aa)
    if expr['act'] == 'div':
        c = float(expr['a'])/float(expr['b'])
        aa = {'value': c}
        return (aa)
    if expr['act'] == 'mult':
        c = int(expr['a'])*int(expr['b'])
        aa = {'value': c}
        return (aa)
    if expr['act'] == 'mult2':
        c = int(expr['a'])**int(expr['b'])
        aa = {'value': c}
        return (aa)
    else:
        return 'NaN'
 
if __name__ == '__main__':
    fcalc.run(debug=True)