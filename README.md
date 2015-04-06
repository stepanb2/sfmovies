Film Locations in San Francisco
=========
##Goal:
Create a service that shows on a map where movies have been filmed in San Francisco. The user should be able to filter the view using auto-completion search.
#####Try it:
[Film Locations in San Francisco](http://52.10.156.184/)
  
### Technologies/libraries:
#####Backend:  
Back-end was implemented on Python using these technologies/libraries:
  1. [Flask](http://flask.pocoo.org/) - haven't used before
  2. [uWSGI](https://uwsgi-docs.readthedocs.org/en/latest/) - haven't used before  
  3. [Redis](http://http://redis.io/) - used before
  4. [GoogleGeocodeAPI](https://developers.google.com/maps/documentation/geocoding/) - haven't used before
  5. [Nginx](http://nginx.org/en/)- haven't used before
  6. [virtualenv](https://virtualenv.pypa.io/en/latest/) - used before
  7. [AWS](http://aws.amazon.com/) - used before
  
#####Web:  
  1. [Bootstrap-3.2.0](http://getbootstrap.com/) - used before
  2. [Backbone](http://backbonejs.org/) - haven't used before
  3. [JQuery](https://jquery.com/) - used before
  4. [Underscore](http://underscorejs.org/) - used before
  4. [RequireJS](http:/http://requirejs.org/) - used before
  5. [GoogleMapsAPI](https://developers.google.com/maps/web/) - haven't used before

###System Design:  
Assumptions that were made in the design:
   1. Small amount of users - only one server is allocated; Google Maps API is used.
   2. Don't need to store and maintain data - that's why a disk based database(like Postgres, MySQL) is not used
   3. Small amount of film locations data - there are around 1k film locations in the [SF OpenData](https://data.sfgov.org/Culture-and-Recreation/Film-Locations-in-San-Francisco/yitu-d5am?). That's why Redis was used. Also this was the reason why a naive full text search was implemented; if the dataset were larger I would use [Apache Solr](http://lucene.apache.org/solr/) or a custom index based full text search implementation
   4. Combination of {film name, release_year, location} is unique - the unique id is generated as the hash of the combination and used across the system. Random id is also possible but makes it harder to define if the same object is already in the system.

Back-end consists of three parts:
  1. Filmlocation Lib - a package that performs all main operations such as: loading data, fulfilling data with the geo coordinates, storing data in Redis, performing search.
  2. Flask Web App - defines JSON API handlers. Handlers use Filmlocation lib and also provide caching layer.
  3. DB Update Task - the python script that uses Filmlocation lib to keep the film locations data in Redis up to date (if new data become available in SF OpenData). It's scheduled to run once per day. It calls update_data() from the Filmlocation which downloads data from SF OpenData, loads geocodes and adds all new data to Redis.

Front-end:
Backbone model and views are used to keep and render film locations data. Data is loaded using jQuery. Google maps are used to show markers with film locations details. Underscore template is used for the marker's window info. jQuery AutoComplete plug-in is used for auto-complete. RequireJs is used to organize import of JS libs.

####Filmlocation Lib: 
#####Install:
Download the repo and run:
```sh
    python scripts/setup.py install
```
#####Sample Usage: 
```python
import redis
import filmlocation

film_lib = filmlocation.FilmLocation(redis_db)
# load films data
raw_data = filmlocation.get_movies_data()
# add data to the db
film_lib.update_data(raw_data)
# query data
result = film_lib.search("Tarantino")
```
####JSON API:

#####Endpoints:
 <table>
    <tr>
        <td>URL</td>
        <td>Method</td>
        <td>Description</td>
    </tr>
    <tr>
        <td>/api/locations/explore</td>
        <td>GET</td>
        <td>Gives a list of randomly selected film locations</td>
    </tr>
    <tr>
        <td>/api/locations/search/?q=<string:query></td>
        <td>GET</td>
        <td>Gives a list of film locations that satisfy the search query</td>
    </tr>
 </table>

###What is missed:  
  1. Logging and monitoring(both usage and error)
  2. Increase reliability of the uWSGI by using [Supervisor](http://supervisord.org/)
  3. Lack of api testing code, performance testing
  4. Server security testing script (e.x.: make sure that redis port is closed, access to admin pages is closed, etc.)
  5. Back button support in the web page

###Deploy:
TODO

###Host:
[Film Locations in San Francisco](http://52.10.156.184/) - http://52.10.156.184/

###Personal:
[Linkedin](https://www.linkedin.com/profile/view?id=75135279)