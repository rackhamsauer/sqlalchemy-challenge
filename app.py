# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
from datetime import datetime
import datetime as dt 
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask('Hawaii')



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/startend<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of precipitation data including the date and prcp of each measurement for the last 12 months"""
    # Find the most recent date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    
    # Calculate the date 12 months before the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary with date as key and prcp as value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    stations = session.query(Measurement.station.distinct()).all()  

    session.close()

    # Create a dictionary from the row data and append to a list of all stations
    all_stations = []
    for station in stations:
        print(station)
        print("**********")
    
        station_dict = {}
        station_dict["station"] = station[0]
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 12 months prior to the most recent date
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    one_year_ago_temp = most_recent_date - pd.DateOffset(years=1)

    # Query the most active station
    most_active_station_id_result = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()

    # Check if the query result is not empty
    if most_active_station_id_result:
        most_active_station_id = most_active_station_id_result[0]
    else:
        session.close()
        return jsonify({"message": "No temperature observations found."}), 404

    # Query the temperature observations (date and tobs) for the most active station within the last 12 months
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.station == most_active_station_id).\
                        filter(Measurement.date >= one_year_ago_temp.strftime('%Y-%m-%d')).all()

    session.close()

    # Create a list of dictionaries containing date and temperature observations
    year_temps = [{"date": date, "tobs": temp} for date, temp in temperature_data]

    return jsonify(year_temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for the given start date
    start_date_temps = session.query(Measurement.date,
                                 func.min(Measurement.tobs),
                                 func.avg(Measurement.tobs),
                                 func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).\
                    group_by(Measurement.date).all()


    session.close()

    # Create a list of dictionaries containing the minimum, average, and maximum temperatures
    start_temps = [{"Date": temp[0],"TMIN": temp[1], "TAVG": temp[2], "TMAX": temp[3]} for temp in start_date_temps]

    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures for the given start and end dates
    start_end_date_temps = session.query(Measurement.date,
                                         func.min(Measurement.tobs),
                                         func.avg(Measurement.tobs),
                                         func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).\
                            group_by(Measurement.date).all()

    session.close()

    # Create a list of dictionaries containing the minimum, average, and maximum temperatures
    start_end_temps = [{"Date": temp[0], "TMIN": temp[1], "TAVG": temp[2], "TMAX": temp[3]} for temp in start_end_date_temps]

    return jsonify(start_end_temps)

@app.route("/api/v1.0/<test>")
def test(test):
    return test
if __name__ == '__main__':
    app.run(debug=True)
