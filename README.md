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
% psql postgres
\q # quits

## Virtual Environment
### Create Virtual Environment and install libraries
```
mkvirtualenv personal_site
pip install -r requirements.txt
deactivate
workon personal_site
python app.py
workon #See all projects

```

## Run Flask server
```
$ export FLASK_APP=p_site.py
$ export DATABASE_URL=postgresql+psycopg2://p_site:<password>@localhost/mdb
# to turn on debug mode
$ export FLASK_ENV=development
$ flask run
$ flask shell
```

## DB Upgrades and migrations
```
flask db migrate -m "details"
flask db upgrade
```

## Setup on server
```
# Had to run this after server reboot to get working
sudo service nginx reload

sudo supervisorctl status
sudo supervisorctl stop p_site
sudo supervisorctl start p_site
```
