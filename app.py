# Import the dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement=Base.classes.measurement
Station=Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Hawaii Climate<br/> "
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using date as the key and prcp as the value.

    Return the JSON representation of your dictionary."""

    # Create our session (link) from Python to the DB
    session=Session(engine)

    # Query the date and precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        all_date_prcp.append(date_prcp_dict)

    return jsonify(all_date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    # Create our session (link) from Python to the DB
    session=Session(engine)
    # Query the station name data
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all stations
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data.
    
    Return a JSON list of temperature observations (TOBS) for the previous year."""

    # Create our session (link) from Python to the DB
    session=Session(engine)
    # Query the ativities of staions and ordered by descending
    station_act=session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Get the most activat station
    query_station=station_act[0][0]
    # Query the temperature observation of the most active station
    # Get the date range
    latest_date_str_stat = session.query(Measurement.date).\
                        filter(Measurement.station == query_station).\
                        order_by(Measurement.date.desc()).first()
    latest_date_stat=dt.datetime.strptime(latest_date_str_stat[0],'%Y-%m-%d')
    query_date_stat=dt.date(latest_date_stat.year -1, latest_date_stat.month, latest_date_stat.day)

    results = session.query(Measurement.tobs).\
            filter(Measurement.date>query_date_stat).\
            filter(Measurement.station == query_station).all()

    # Unpack the data
    all_tobs = list(np.ravel(results))

    session.close()

    return jsonify(all_tobs)    


@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start.

    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query the data in the date range
    sel=[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results=session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all date
    tinfos = []
    for date, tmin, tavg, tmax in results:
        tinfo = {}
        tinfo["DATE"] = date
        tinfo["TMIN"] = tmin
        tinfo["TAXG"] = tavg
        tinfo["TMAX"] = tmax
        tinfos.append(tinfo)

    return jsonify(tinfos)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.

    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the data in the date range
    sel=[Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results=session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).\
            group_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all date
    tinfos = []
    for date, tmin, tavg, tmax in results:
        tinfo = {}
        tinfo["DATE"] = date
        tinfo["TMIN"] = tmin
        tinfo["TAXG"] = tavg
        tinfo["TMAX"] = tmax
        tinfos.append(tinfo)

    return jsonify(tinfos)

if __name__ == '__main__':
    app.run(debug=True)




