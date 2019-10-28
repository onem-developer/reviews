### Quickstart

Works with Python 3.7. Preferably to work in a virtual environment, use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) to create a virtual environment.

1. `mkvirtualenv reviews --python=`which python 3.7`
2. `sudo apt-get install python3.7-dev`

1. `git clone git@github.com:onem-developer/reviews.git`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`
7. `ngrok http 8000`

### Testing the app

Register the app on the ONEm developer portal (https://testtool.dhq.onem:6060/);
Set the callback URL to the forwarding address obtained from ngrok's output;
Go to https://testtool.dhq.onem/ and send the registered name with # in front.

### Important
The local sqlite database is already populated with 3 items.
So, when you start the service you should see the below menu and already be able to rate or comment:
```
--------------------
#(app_name) REVIEWS HOME
A item 1
B item 2
C item 3
--Reply A-C
--------------------
```


### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
