import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create a database session object
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home page
@app.route("/")
# List all routes that are available.
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the date and precipitation scores
    date_prcp_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= query_date).all()
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_dict = dict(date_prcp_data)
    # Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    #Design a query to retrieve the stations
    stations = session.query(station.station).distinct().all()
    #Return a JSON list of stations from the dataset.
    return jsonify(stations)

# Temperature Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= query_date).\
        filter(measurement.station == 'USC00519281')
    all_tobs = []
    for date, tobs in active_station:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        all_tobs.append(tobs_dict)
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(all_tobs)

# Start Only Route
@app.route("/api/v1.0/<start>")
def start_date_data(start):
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        group_by(measurement.date).all()
    return_json=[]
    for each_result in results:
        return_json.append([each_result[0], each_result[1], each_result[2], each_result[3]])
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    return jsonify(return_json)

#Start and End Route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    results_end = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end)
        #group_by(measurement.date).all()
    return_end_json=[]
    for each_result in results_end:
        return_end_json.append([each_result[0], each_result[1], each_result[2], each_result[3]])

# Close session
session.close()

if __name__ == "__main__":
    app.run(debug=True)
