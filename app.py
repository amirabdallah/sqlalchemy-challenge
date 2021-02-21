# 1. import Flask & Jsonify
import datetime as dt
import numpy as np
import pandas as pd


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# 2. Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# 3. Create an app, being sure to pass __name__
app = Flask(__name__)

# 4. Define what to do when a user hits the index route
@app.route("/") 
def home():
    print("Server received request for 'Home' page...")
    return (
            f"/api/v1.0/precipitation </br>"
            f"/api/v1.0/stations </br>"
            f"/api/v1.0/tobs </br>"
            f"/api/v1.0/<start> and /api/v1.0/<start>/<end>`"
    )
# 5. Define route for the Precipitation's page
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Percipitation' page...")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query Percipitation and date of perceiptitation for the past 12 months.
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > '2016-12-31').all()

    session.close()

    # Create a dictionary from the row data and append to a list of Measurements
    all_measurements = []
    for date, prcp in precipitation:
        percipitation_dict = {}
        percipitation_dict["date"] = date
        percipitation_dict["prcp"] = prcp
        all_measurements.append(percipitation_dict)

    return jsonify(all_measurements)
# 6. Define route for the Stations page
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to show how many stations are available in this dataset?
    stations_query = session.query(Station.station,Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of Measurements
    stations = []
    for station, name in stations_query:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations.append(stations_dict)

    return jsonify(stations)
# 7. Define route for tobs API
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    reduced_range = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_query = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > reduced_range).all()

    session.close()

    # Create a dictionary from the row data and append to a list of Measurements
    temps = []
    for tobs in tobs_query:
        temp_dict = {}
        temp_dict["tobs"] = tobs
        temps.append(temp_dict)

    return jsonify(temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Create our session (link) from Python to the DB
    session = Session(engine)

    if not end:
        query = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results
        temps = list(np.ravel(query))
        return jsonify(temps)

    query = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
    
    temps = list(np.ravel(query))
    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run(debug=True)
