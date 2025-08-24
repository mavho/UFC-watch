# UFC API and Fight Predictor
This is an easily accessible RESTFUl api written with Flask. The main goals was to provide a service where users can get bout information and stricking statistics on UFC events. Coupled with the API is a fight prediction module written with Scikit Learn. It's a fairly straight foward model, it uses linear regression to calculate whether or not a fighter would win.

### This API is still under active development. See bottom

#### Is the information accurate?
I used a webscrapper to scrape information of the ufcstats page. I only grabbed around half of the most recent events, so there are going to be some events that are missing. This info is as accurate as that page. Aside from that it is accurate.

## Technologies
I used a multitude of libraries and frameworks to complete this. The most noteable are [Flask](https://flask-restful.readthedocs.io/en/latest/) for the webservice framework, [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for the creating the webscrapper, and [scikit-learn](https://scikit-learn.org/stable/). The front end uses the [Bulma](https://bulma.io/documentation/) CSS framework.


## API routes
These endpoints will return a JSON encoded string.
If you're using Javascript, you can issue an XMLHttpRequest, then
```
var json_obj = JSON.parse(payload);
```

### Events
You can issue a GET request to the events endpoint:
```
curl -s --request GET --header Content-Type: application/json --write-out \n%{http_code}\n http://13.52.239.45/api/events/all
```
Specifying all will grab all the events with their corresponding name, location, date, and event id.

### Event
The event endpoint has the form
```
/api/event/id
```
The json returned has two keys, bouts and event data.
### Predictions
You can get the latest event predictions from the predictions endpoint
```
/api/predictions
```

### To Upgrade table schema

If there are updates to the model, we use Flask-Alembic to upgrade the SQL database.
Export out the `$FLASK_APP=ufc.api.py`.
Run `flask db revision --autogenerate -m "Change comment"`
Then review the script and apply them. Test out upgrade and down grade with
`flask db upgrade` or `flask db downgrade`


### Generating Proxy list


##### TODO's
- prediction route with 2 fighters (started)
- fighters endpoint
