# flask_calc
# на Debian 8

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install flask_sqlalchemy
sudo apt-get install rabbitmq-server
sudo pip3 install celery
sudo apt-get install sqlite3

sudo service rabbitmq-server start #запускаем брокер
celery -A tasks worker --loglevel=info # запускаем celery c вывдом отладочной информации

#создаем базу
cd /tmp/ 
sqlite3 test.db

#В сессии python в рабочем каталоге приложения инициализируем базу.
	>>from fcalc import db
	>>db.create_all()

python3 fcalc.py #запускаем.
