# personal_site
My Personal Website for information about me and to track my Fitness

## Postgres database
### Start
```
pg_ctl -D /usr/local/var/postgres start
# Start Postgres and set Brew to start it on bootup
pg_ctl -D /usr/local/var/postgres start && brew services start postgresql
```

### Access postgresql from terminal
```
% psql postgres
% psql -d mdb #Access database mdb with current user
\q # quits
```

## Virtual Environment
### Create Virtual Environment and install libraries
```
mkvirtualenv personal_site
pip install -r requirements.txt
deactivate
workon personal_site
source personal_site/bin/activate
python app.py
workon #See all projects

python3 -m venv $HOME/.virtualenvironments/p_site
source $HOME/.virtualenvironments/p_site/bin/activate
pip install -r requirements.txt
pip install wheel
deactivate
```

#### On server activate venv
```
source personal_site/bin/activate
```

## Run Flask server
```
$ export FLASK_APP=p_site.py
# to turn on debug mode
$ export FLASK_ENV=development
$ flask run
$ flask shell
```

## Setup on server
```
gunicorn -b localhost:8000 -w 4 p_site:app

# Had to run this after server reboot to get working
sudo service nginx reload

sudo supervisorctl status
sudo supervisorctl reload
sudo supervisorctl stop p_site
sudo supervisorctl start p_site
```
