import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return ("Welcome to my page <br>"
            "Available Routes:<br>"
            "/precipitation<br>"
            "/stations<br>"
            "/temperature<br>"
)
@app.route("/precipitation")
def Precipitation():
    Session = sessionmaker(bind=engine)
    session = Session()

    most_recent_point = session.query(func.max(Measurement.date)).scalar()
    year = dt.datetime.strptime(most_recent_point,"%Y-%m-%d") - dt.timedelta(days=375)
    data_prec_score=session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.asc()).\
        filter(Measurement.date>=year.date()).all()    
    precipitation_data = [{"date": date, "prcp": prcp} for date, prcp in data_prec_score]
    session.close()

    return jsonify("precipitation_data")

@app.route("/stations")
def Station():
    Session = sessionmaker(bind=engine)
    session = Session()

    total_stations = session.query(Station.station).count()
    station_active=session.query(Measurement.station,func.count(Measurement.station)).\
                       group_by(Measurement.station).\
                       order_by(func.count(Measurement.station).desc()).all()
    station_data = [{"station": station, "count": count} for station, count in station_active]
    session.close()

    return jsonify("Station_data")

@app.route("/temperature")
def Temperature():
    Session = sessionmaker(bind=engine)
    session = Session()

    temp_summany = session.query(func.max(Measurement.tobs),
                            func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
                            filter(Measurement.station==station_active[0][0]).all()
    
    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).\
                       group_by(Measurement.station).\
                       order_by(func.count(Measurement.station).desc()).first()
    most_active_station_first = most_active_station[0]

    temp_station = session.query(Measurement.tobs).order_by(Measurement.date.asc()).\
               filter(Measurement.date>=year.date()).\
               filter(Measurement.station == most_active_station_first).all()
    
    temp_data = [{"tobs": tobs} for tobs in temp_station]

    session.close()

    return jsonify("temp_data")

if __name__ == '__main__':
    app.run(debug=True)