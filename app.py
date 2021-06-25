import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
#DATABASE SETUP
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

#REFLECT DATABASE INTO NEW MODEL
Base = automap_base()

#REFLECT TABLES
Base.prepare(engine, reflect=True)

#SAVE REFERENCES TO TABLES
Measurement = Base.classes.measurement
Station = Base.classes.station

#CREATE SESSION PYTHON TO DB
session = Session(engine)

#################################################
#FLASK SETUP
#################################################
app = Flask(__name__)

#################################################
#DISPLAY ROUTES
#################################################

@app.route("/")
def welcome():
    """All api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """precipitation data for the last year."""
    #CALCULATE DATE
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #QUERY FOR DATE AND PRECIP FOR LAST YEAR
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_prior).all()

    #DICTIONARE DATE/KEY PRECIPITATION/VALUE
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """List stations."""
    result = session.query(Station.station).all()

    stations = list(np.ravel(result))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """(tobs) for year prior."""
    #CALCULATE DATE
    year_prior = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #QUERY PRIMARY STATION
    result = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_prior).all()

    #UNRAVEL
    temperatures = list(np.ravel(result))

    #RETURN
    return jsonify(temperatures=temperatures)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    #SELECT STATEMENT
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        
        result = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        temperatures = list(np.ravel(result))
        return jsonify(temperatures)

    #CALCULATE TMIN, TAVG, TMAX 
    result = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    #UNRAVEL 
    temperatures = list(np.ravel(result))
    return jsonify(temperatures=temperatures)


if __name__ == '__main__':
    app.run()

