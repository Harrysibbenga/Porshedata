import os
import csv
from flask import Flask, render_template, redirect, url_for, request
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

# gets file path fron computer being used
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/input_data', methods=['GET', 'POST'])
def input_data():

    # Takes the inputs on the dashbord page for the purpose of building a collection in the mlab database
    # This route also changes the name for the collection so it is relevant to the track, year and session.
    # It also takes the file path from the input form in the dashboard template.
    # has functionality to save the file into the csvfiles folder and deletes the file so less memory is used when uploading many files.

    target = os.path.join(APP_ROOT, 'csvfiles/')

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("filepath"):
        filename = file.filename
        destination = "/".join([target, filename])
        file.save(destination)

        if request.method == 'POST':

            track_name = request.form.get('track_name').lower()
            year = request.form.get('year')
            section = request.form.get('section')
            filepath = "csvfiles/"+filename
            dbname = track_name+str(year)+'_'+section

            with open(filepath, "r") as csvfile:
                csvreader = csv.reader(csvfile, delimiter=";", quotechar="/")
                for row in csvreader:
                    mongo.db.dbname.insert(
                        {
                            "driver_number": row[1],
                            "lap_number": row[2],
                            "lap_time": row[3],
                            "lap_improvement": row[4],
                            "top_speed": row[18],
                            "driver_name": row[19],
                            "class": row[21],
                            "team": row[23],
                            "year": year,
                            "track_name": track_name
                        }
                    )
                # removes generic table names document
                mongo.db.dbname.delete_one({"driver_name": "DRIVER_NAME"})
                mongo.db.dbname.rename(dbname)

            # delets the file after its uploaded to the database.
            os.remove(destination)

    return render_template("dashboard.html")


@app.route('/')
def index():
    practice_1 = mongo.db.silverstone2019_practice_1
    practice_2 = mongo.db.silverstone2019_practice_2
    qualifying = mongo.db.silverstone2019_qualifying
    race = mongo.db.silverstone2019_race

    names = get_names(practice_1.find())

    for name in names:

        lap_time = get_data_and_append_to_list(
            practice_1.find(), 'lap_time', name)
        lap_number = get_data_and_append_to_list(
            practice_1.find(), 'lap_number', name)
        driver_number = get_data_and_append_to_list(
            practice_1.find(), 'driver_number', name)
        lap_improvement = get_data_and_append_to_list(
            practice_1.find(), 'lap_improvement', name)
        top_speed = get_data_and_append_to_list(
            practice_1.find(), 'top_speed', name)

        mongo.db.drivers.insert({
            "driver_name": name,
            # "class": driving_class,
            # "team": team,
            'tracks': {
                # "year": year,
                # "track_name": track_name,
                "driver_numbers": driver_number,
                "lap_numbers": lap_number,
                "lap_times": lap_time,
                "lap_improvements": lap_improvement,
                "top_speeds": top_speed,
            }
        })

    return render_template("index.html", practice_1=practice_1.find(), practice_2=practice_2.find(), qualifying=qualifying.find(), race=race.find())

# functions


def get_names(coll):
    # This function loops through the collection and makes a list of driver names in the dataset and returns it
    # coll gets the collection name
    names = []
    for d in coll:
        name = d['driver_name']
        if name not in names:
            names.append(name)
    return names


def get_data_and_append_to_list(coll, field, name):
    # This function loops thorugh the collection and makes a list for a specific feild in the dataset and returns it
    # coll gets the collection name
    # field is the feild that we would like to query
    # name is going to the name of the driver
    arr = []
    for d in coll:
        data = d[field]
        if d['driver_name'] == name:
            arr.append(data)
    return arr


if __name__ == '__main__':
    app.run(debug=True)
