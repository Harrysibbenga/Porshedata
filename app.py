import os
import csv
from flask import Flask, render_template, redirect, url_for, request
from flask_pymongo import PyMongo
from bson import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

# gets file path fron computer being used
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/input_data', methods=['GET', 'POST'])
def input_data():
    drivers = mongo.db.drivers
    driver_names = get_names(drivers.find())
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
                            "track_name": track_name,
                            "round": section,
                        }
                    )
                # Removes generic table names in the document
                mongo.db.dbname.delete_one({"driver_name": "DRIVER_NAME"})
                # Gets the names of all the drivers in the collection
                names = get_names(mongo.db.dbname.find())

                for name in names:
                    # this loop compairs the name of the drivers in the uploaded collection and the drivers collection
                    # if the driver is not in the loop then a new record will be made for the new driver
                    # other wise the track information is updated for the existing one.
                    lap_time = get_data_and_append_to_list(
                        mongo.db.dbname.find(), 'lap_time', name)
                    lap_number = get_data_and_append_to_list(
                        mongo.db.dbname.find(), 'lap_number', name)
                    driver_number = get_data_and_append_to_list(
                        mongo.db.dbname.find(), 'driver_number', name)
                    lap_improvement = get_data_and_append_to_list(
                        mongo.db.dbname.find(), 'lap_improvement', name)
                    top_speed = get_data_and_append_to_list(
                        mongo.db.dbname.find(), 'top_speed', name)

                    year = get_value_from_collection(
                        mongo.db.dbname.find(), 'year', name)

                    round_name = get_value_from_collection(
                        mongo.db.dbname.find(), 'round', name)

                    team = get_value_from_collection(
                        mongo.db.dbname.find(), 'team', name)

                    driving_class = get_value_from_collection(
                        mongo.db.dbname.find(), 'class', name)

                    track_name = get_value_from_collection(
                        mongo.db.dbname.find(), 'track_name', name)

                    if name not in driver_names:

                        mongo.db.drivers.insert({
                            "driver_name": name,
                            "class": driving_class,
                            "team": team,
                            "profile_image": '',
                            "date_of_birth": '',
                            "born": '',
                            "lives": '',
                            'tracks': [
                                {
                                    'round': round_name,
                                    'year': year,
                                    "track_name": track_name,
                                    "driver_numbers": driver_number,
                                    "lap_numbers": lap_number,
                                    "lap_times": lap_time,
                                    "lap_improvements": lap_improvement,
                                    "top_speeds": top_speed,
                                }
                            ]
                        })
                    else:
                        mongo.db.drivers.update(
                            {"driver_name": name},
                            {"$push": {'tracks': {
                                'round': round_name,
                                'year': year,
                                'track_name': track_name,
                                'driver_numbers': driver_number,
                                'lap_numbers': lap_number,
                                'lap_times': lap_time,
                                'lap_improvements': lap_improvement,
                                'top_speeds': top_speed,
                            }}})
                # this is to delete the tempral collection created by uploading the csv file.
                mongo.db.dbname.drop()
                # delets the file after its uploaded to the database.
                os.remove(destination)

    return render_template("dashboard.html", drivers=drivers.find())


@app.route('/view_driver', methods=['GET', 'POST'])
def view_driver():
    selected_name = request.form.get("driver")
    driver = mongo.db.drivers.find_one({'driver_name': selected_name})
    return render_template("view.html", driver=driver)


@app.route('/edit_driver/<driver_id>', methods=['GET'])
def edit_driver(driver_id):
    driver = mongo.db.drivers.find_one({'_id': ObjectId(driver_id)})
    return render_template('editdriver.html', driver=driver)


@app.route('/update_driver/<driver_id>', methods=['GET', 'POST'])
def update_driver(driver_id):
    driver = mongo.db.drivers.find_one({'_id': ObjectId(driver_id)})
    target = os.path.join(APP_ROOT, 'static/images/drivers')

    for file in request.files.getlist("profile_image"):
        filename = file.filename
        destination = "/".join([target, filename])
        file.save(destination)

        if request.method == 'POST':
            date_of_birth = request.form.get('date_of_birth')
            born = request.form.get('born')
            lives = request.form.get('lives')
            team = request.form.get('team')
            mongo.db.drivers.update_one(
                {'_id': ObjectId(driver_id)},
                {'$set':
                    {
                        'date_of_birth': date_of_birth,
                        'born': born,
                        'lives': lives,
                        'team': team,
                        'profile_image': filename
                    }
                 }
            )
    return render_template('view.html', driver=driver)


@app.route('/')
def index():
    drivers = mongo.db.drivers.find()
    return render_template("index.html", drivers=drivers)

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


def get_value_from_collection(coll, field, name):
    # This function loops thorugh the collection and makes a list for a specific feild in the dataset and returns it
    # coll gets the collection name
    # field is the feild that we would like to query
    # name is going to the name of the driver
    value = ''
    for d in coll:
        if d['driver_name'] == name:
            value = d[field]
    return value


if __name__ == '__main__':
    app.run(debug=True)
