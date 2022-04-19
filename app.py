# Importing the dependencies
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

# Importing the dependencies to help access SQLite database
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Setting up the database engine for the flask application
# which allows us to access and query the SQLlite database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflecting an exisiting DATABASE into a new model/classes
Base = automap_base()

# Reflecting the TABLES/ SCHEMA of the SQLlight database and create mappings
Base.prepare(engine, reflect=True)

# To view all the classes/ different tables automaped
Base.classes.keys()

# Creating a variable that references each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to our database
# Allows us to query for data
session = Session(engine)

# Creating a new Flask app instance
# '__name__ is a special chracter that set itself to be the file name
app = Flask(__name__)

@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API! <br>
    Climate link: http://127.0.0.1:5000/ <br>
    <br>
    ... <br>
    <br>
    Available Routes: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/temp/start/end <br>
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculating the date of one year ago from the indicated date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Creating a query to return the date and precipitations for all the days in the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # Creating an dictionary that returns the date as a key and the precipitation
    precip = {date: prcp for date, prcp in precipitation}

    # To format it properly, we will jsonify the object - formats it like a json file
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Creating a query ti retieve all the stations in the database
    results = session.query(Station.station).all()

    # results is in the form of lists containing multiple lists - we will unravel this data into one lists using the np.ravel() function
    stations = list(np.ravel(results))

    # returning the jsonified version of stations
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Like before, we are calculating the date one year ago from the last date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Creating a query that returns all the temperatures observed from the primary station (filter 1) and from within the last year (filter 2)
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prev_year).all()

    # We will unravel the results, jsonify it, then assign it to an object
    temps = list(np.ravel(results))

    # jsonifying temps then returning it
    return jsonify(temps=temps)

# Creating a route in which we will report the (min/avg/max) temps between a given range of dates. The brackets in the route are for users to input a variable for start/end days
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# We have to set two parameters, start and end
def stats(start=None, end=None):

    # Querying to select the desired data from our SQLite database. inputting the data into a list
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)] #func objects allows us to query with special functions

    # To help filter, runs all the dates until the end data is reached
    if not end:

        # Using the session object to query our SQLight database - the '*' indicates multiple results for the data we are looking for (min/avg/max) temps
        results = session.query(*sel).filter(Measurement.date >= start).all() # filter looking at all dates passed our indicated start date
        
        # Unraveling the results and returning a jasonified version
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps)



#http://127.0.0.1:5000/