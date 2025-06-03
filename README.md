# personal_site
My Personal Website for information about me and to track my Fitness

## Postgres database
### Start
```
pg_ctl -D /usr/local/var/postgres start
# Start Postgres and set Brew to start it on bootup
pg_ctl -D /usr/local/var/postgres start && brew services start postgresql

# If need to kill postgres
pg_ctl -D /usr/local/var/postgres status
pg_ctl -D /usr/local/var/postgres kill TERM 35775 
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
pip install gunicorn
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
## Update Packages
1. In requirements.txt file change all == to >=
2. Activate Virtual Environment, on server
``` 
source personal_site/bin/activate
```
3. Update pip and packages
```
$ pip install --upgrade pip
$ pip install --upgrade -r requirements.txt
```
4. Confirm packages are now at expected version numbers
```
pip freeze
```
5. Restart server
```
flask run or psite_start
```
6. Validate website is working
  * Workouts page loads
  * A Workout page loads, can see map details and run graph
  * Dashboard and graphs load successfully
  * Can upload a new workout
7. Fix any bugs as needed
8. After validations commit changes to github
9. Pull requirements.txt and bug fixes to server
10. Perform same steps 3 through 6

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
