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
