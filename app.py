import os
import csv
from flask import Flask, render_template, redirect, url_for, request
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://harry:porsche_data1@ds161032.mlab.com:61032/porsche_data?retryWrites=false"
mongo = PyMongo(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# total_points_arr = []
# total_wins_arr = []
# for track in driver["track"]:
#     total_points_arr.append(track['points'])
#     if track["position"] == 1:
#         total_wins_arr.append(track["position"])
#         total_wins = sum_array(total_wins_arr)
#     drivers.update_one({"lastname": driver["lastname"]}, {
#         "$set": {"total_wins": int(total_wins)}})
# total_points = sum_array(total_points_arr)
# drivers.update_one({"lastname": driver["lastname"]}, {
#     "$set": {"total_points": int(total_points)}})
# all_drivers = drivers.find()

# helper functions


def sum_of_array(arr):

    # this function takes an array and returns the sum of all the values within the array

    return(sum(arr))


def get_driver_championships(drivers, all_drivers, championship_name, years_in_championship_name, total_years_in_championship_name):

    # this function takes the:
    # - drivers collection and cursor object of all_dirvers
    # - the championship_name that needs queriying
    # - years_in_championship_name which will be updated in the database as an array
    # - total_years_in_championship_name which will be updated as an integer in the database

    # for the purpose of searching all drivers for a specific championship name within the database and generating the
    # years the driver has been in that championship including the amount of times they have entered that championship (case sensitive)
    # returning an updated value of all_drivers in the database

    # makes sure that the value insert in the array isnt duplicated

    years_in_champ_arr = []

    for driver in all_drivers:

        for championship in driver["championships"]:

            if championship["name"] == championship_name:
                if not championship["year"] in years_in_champ_arr:
                    years_in_champ_arr.append(championship["year"])

        total_years_in_champ = len(years_in_champ_arr)

        drivers.update_one({"lastname": driver["lastname"]}, {
            "$set": {years_in_championship_name: years_in_champ_arr, total_years_in_championship_name: total_years_in_champ}
        })

        all_drivers = drivers.find()

        return all_drivers


# def podiums(drivers, all_drivers):
#     podiums = []
#     for driver in all_drivers:
#         print(driver['rounds'])
#     # podiums = sum_of_array(podiums)


@app.route('/input_data', methods=['GET', 'POST'])
def input_data():

    # Takes the inputs on the dashbord page for the purpose of building a collection in the mlab database
    # This route also changes the name for the collection so it is relevant to the track, year and session.
    # It also takes the file path from the input form in the dashboard template.
    # has functionality to save the file into the csvfiles folder after wards it deletes the file so less memory is used when uploading many files.

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
    practice_1 = mongo.db.silverstone2019_practice_1.find()
    practice_2 = mongo.db.silverstone2019_practice_2.find()
    qualifying = mongo.db.silverstone2019_qualifying.find()
    race = mongo.db.silverstone2019_race.find()

    return render_template("index.html", practice_1=practice_1, practice_2=practice_2, qualifying=qualifying, race=race)


if __name__ == '__main__':
    app.run(debug=True)
