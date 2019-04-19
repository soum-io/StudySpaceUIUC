from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from .models import Student, Library, Request, FloorSection, hoursOfOp, recordData
import pandas as pd
import googlemaps
import requests
import operator
import numpy as np
from itertools import tee
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.db.models import Avg
import sys


# how to pass to page to page if user is logged in or not. This is really bad
# for privacy as there is much more secure ways to do this. If there is time
# before the final presentation, this will be fixed
logged_in = {"isLoggedIn": False, "username": ""}

API_key = 'AIzaSyBzozWYI3q9hIHEOh1arRxsMLLzYx83MLQ'
GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'


# convert string time to military time
def convertTime(string_time):
    if string_time == "":
        return -1
    num, half = string_time.split(" ")
    add_on = 0
    if(half == "PM"):
        add_on = 1200
    hour, min = num.split(":")
    hour = int(hour)
    min = int(min)
    finalTime = hour*100+min+add_on
    if(str(finalTime)[-2] == "3"):
        finalTime = finalTime - 30 # no support for 30 minutes right now
    return finalTime

# converts "mm/dd/yyyy" to day of week
def getDay(forDate):
    if(forDate == ""):
        return -1
    date_obj = pd.to_datetime(forDate, format="%m/%d/%Y")
    day_int = date_obj.weekday() + 1
    return day_int

# Create your views here.
def login_view(request, *args, **kwargs):
    global logged_in
    logged_in = {"isLoggedIn":False, "username":""} # pass to html for navbar
    return render(request, "login/login.html", {"logged_in":logged_in})


def signup_view(request, *args, **kwargs):
    global logged_in
    logged_in = {"isLoggedIn":False, "username":""} # pass to html for navbar
    return render(request, "signup/signup.html", {"logged_in":logged_in})


def search_view(request, *args, **kwargs):
    global logged_in
    # check if we are requesting from login or annonomous user.
    if(request.method == "POST"): # post are from login

        # check if request is from a user signup or login
        signup_request = "location" in request.POST # this is only a field in the signup form

        if("UpdatedAddress" in request.POST): # coming from updated address
            print("updating raw address")
            updatedAddress = request.POST["UpdatedAddress"]
            student_username = logged_in["username"]
            print(student_username)
            print(updatedAddress)
            update_query = 'UPDATE pages_Student SET "mainAddress" = %s WHERE "username" = %s;'
            with connection.cursor() as cursor:
                cursor.execute(update_query, (updatedAddress, student_username))
            default_address = updatedAddress
            # TODO update student's address with student_username
            return render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})

        elif(signup_request): # coming from signup

            # get singup form data
            email = request.POST["email"]
            location = request.POST["location"]
            password = request.POST["password"]
            passwordAgain = request.POST["passwordAgain"]

            # TODO: Check that the provided signup information sufficient. If so, add user to the database
            valid_signup = False
            if email != "" and location != "" and password != "" and password == passwordAgain:
                passHash = make_password(password)

                insert_query = 'INSERT INTO pages_student ("username", "passwordHash", "mainAddress", "prefStudyEnv", "favLibrary", "major", "isAdmin") VALUES (%s, %s, %s, \'\', \'\', \'\', %s);'
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (email, passHash, location, "FALSE"))
                print("Student Registered")
                valid_signup = True

            if(valid_signup): # user is created now redirect to search
                default_address = location
                logged_in = {"isLoggedIn":True, "username":email} # pass to html for navbar
                return  render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})
            else: # signup fields are not valid
                logged_in = {"isLoggedIn":False, "username":""} # pass to html for navbar
                return render(request, "login/login.html", {"logged_in":logged_in})
        else:    # coming from login
            print(request.POST)

            # get login form data
            email = request.POST["email"]
            password = request.POST["password"]

            #TODO: check if username and password match database of user
            matches = False
            default_address = ""
            try:
                temp_student = Student.objects.raw('SELECT * FROM pages_Student WHERE "username" = %s', [email])[0]
                if check_password(password, temp_student.passwordHash):
                    print("Success Match")
                    matches = True
                    default_address = temp_student.mainAddress
            except ObjectDoesNotExist:
                matches = False
                default_address = ""

            if(matches): # if user if valid
                logged_in = {"isLoggedIn":True, "username":email} # pass to html for navbar
                return  render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})
            else: # user is not valid
                logged_in = {"isLoggedIn":False, "username": ""} # pass to html for navbar
                return render(request, "login/login.html", {"logged_in":logged_in})

    else: # get from anon or entering another search from results page user
        default_address = ""
        try:
            curr_user = Student.objects.raw('SELECT * FROM pages_Student WHERE "username" = %s', [logged_in["username"]])
            if len(curr_user) != 0:
                curr_user = curr_user[0]
                default_address = curr_user.mainAddress
            else:
                default_address = ""
        except ObjectDoesNotExist:
            default_address = ""

        #TODO if user is logged in - fill in their default address to defailt address var.
        return render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})

def get_google_maps_distances(origin):
    library_df = pd.DataFrame(list(Library.objects.all().values('libName', 'libAddress', 'reservationLink')))

    gmaps = googlemaps.Client(key=API_key)
    destinations = list(library_df['libAddress'])
    matrix = gmaps.distance_matrix(origin, destinations, mode="walking", units="imperial")
    elems = matrix["rows"][0]["elements"]
    distances = []
    distance_words = []
    for dist in elems:
        lib_distance = dist["distance"]['value']
        lib_distance_words = dist["distance"]["text"]
        distances.append(lib_distance)
        distance_words.append(lib_distance_words)
    library_df['Distance'] = distances
    library_df['Distance Words'] = distance_words

    #get distance rankings... add to library_df['distrank']
    dist_rankings = {}
    rankings = [0,0,0,0,0]
    iter = 0
    for i in range(len(rankings)):
        best_index = distances.index(min(distances))
        rankings[best_index] = i+1
        distances[best_index] = 0
    library_df['distrank'] = rankings

    return library_df

def get_open_sections_func(dayOfWeek, forTimeInt, environment):
    get_open_sections = 'SELECT * FROM pages_FloorSection as FS, pages_hoursOfOp as hours WHERE hours."dayOfWeek" = %s and hours."libName" = FS."libName" and hours."openTime" <= %s and hours."closeTime" >= %s and FS."studyEnv" = %s'
    with connection.cursor() as cursor:
        cursor.execute(get_open_sections, (str(dayOfWeek), str(forTimeInt), str(forTimeInt), environment))
        open_sections = cursor.fetchall()
    return open_sections

def results_view(request, *args, **kwargs):
    global logged_in

    if(request.method == "POST"): # post are from login
        # check if request is from a user signup or login
        if("UpdatedAddress" in request.POST): # coming from updated address
            updatedAddress = request.POST["UpdatedAddress"]
            student_username = logged_in["username"]
            update_query = 'UPDATE pages_Student SET "mainAddress" = %s WHERE "username" = %s;'
            with connection.cursor() as cursor:
                cursor.execute(update_query, (updatedAddress, student_username))
            default_address = updatedAddress
            # TODO update student's address with student_username
            return render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})

    print(request.GET)
    # get search form data
    location = request.GET["location"] # address as string address, not coordinates
    # groupSize = request.GET["groupSize"] # will be a digit in string format
    groupSize = 1
    forDate = request.GET["forDate"] # format is "mm/dd/yyyy"
    dayOfWeek = getDay(forDate)# turns date into day of week int 1 - 7 with 1 = "Monday"
    forTime = request.GET["forTime"] # format is "01:00 AM"
    forTimeInt = convertTime(forTime) # int version of requested time. so "05:30 PM" becomes 1730.
    print("time: " + str(forTimeInt))
    print("Day of week: " + str(dayOfWeek))
    environment = request.GET["enviroment"] # will either be "Quiet Open Study", "Quiet Closed Study", or "Group Study"

    #if query is invalid redirect back to serach page
    if location == "" or groupSize == "" or forDate == "" or forTime == "" or environment == "":
        default_address = ""
        if location != "":
            default_address = location
        return render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})

    library_df = get_google_maps_distances(location)
    open_sections = get_open_sections_func(dayOfWeek, forTimeInt, environment)
    min_distance = sys.float_info.max
    for idx, row in library_df.iterrows():
        print(row["libName"], row["Distance"])
        if row["Distance"] < min_distance:
            min_distance = row["Distance"]

    confidences = {}
    spot_confidences = {}
    #get percent fulls for each floor_section -> then calc confidence
    for floor_section in open_sections:
        max_cap = floor_section[4]
        libName = floor_section[1]
        floorNum = floor_section[2]
        section = floor_section[3]

        get_current_students = list(recordData.objects.filter().aggregate(avg_count = Avg('count')).values())
        get_current_students_raw = 'SELECT AVG(count) as avg, pages_recordData."recordID" FROM pages_recordData WHERE "libName" = %s AND "floorNum" = %s AND "section" = %s AND "dayOfWeek" = %s AND time = %s GROUP BY pages_recordData."recordID";'
        students_predicted_raw = recordData.objects.raw(get_current_students_raw, [libName, str(floorNum), section, str(dayOfWeek), str(forTimeInt)])

        avg_count = 0.0
        for record in students_predicted_raw:
            avg_count += record.count

        if len(students_predicted_raw) != 0:
            avg_count /= len(students_predicted_raw)

        percent_full = avg_count/max_cap
        #get to end confidence from percent full and distrank
        dist_weight = 0.25
        capacity_weight = 1 - dist_weight
        #25% distance = distweight
        # if closest library, all floorsections get distweight from distance
        # second closest gets 0.8*distweight
        # third = 0.6*distweight
        # fourth = 0.4*distweight
        # fifth = 0.2*distweight
        # effectively = (6-distrank)*distweight
        #lib_row = library_df[library_df["libName"] == libName]
        #calculate %further away this library is from closest one
        d = library_df.loc[library_df['libName'] == libName, 'Distance'].iloc[0]

        percent_distance = 1 - (d - min_distance)/d

        #distrank = library_df.loc[library_df['libName'] == libName, 'distrank'].iloc[0]
        #print(distrank)
        #75% percent_full = full_weight
        #each floor section gets %full*full_weight
        #confidence = dist_weight*(6-distrank)/5 + capacity_weight*(1-percent_full)
        confidence = percent_distance*dist_weight + capacity_weight*(1 - percent_full)
        confidences[floor_section] = confidence
        spot_confidences[floor_section] = 1 - percent_full

    sorted_confidences = sorted(confidences.items(), key=operator.itemgetter(1), reverse = True)
    # TODO: Use search information to get reccomendations. Each reccomendation need to contain the following information:
    # 1. library abbreviation ("UGL","GG","MainLib", "Chem", "Aces") -> "lib"
    # 2. Floor (e.g. "4" for fourth floor) -> "floor"
    # 3. Floor Section (Like left or right or however else we store it) -> "section"
    # 4. How far the library is from the location the user entered (e.g. "20M" for 20 miles) -> "dist"
    # 5. Boolean if the section is quiet or not -> "quiet"
    # 6. How confident we are. (e.g. "70" or "50", should be as a percentage) -> "conf"
    # 7. Rank of the result (1-5), as srting -> "rank"
    # 8. Library room reservation link -> "link"

    # put the recommendations in the following dictionary allResults. When ready, remove the two
    # results in their with the number of results the algorithm returns.
    allResults = {}
    res = "result"
    count = 1
    for section, confidence in sorted_confidences:
        if count == 6:
            break
        result = {}
        if section[1] == "Grainger":
            result["lib"] = "GG"
        elif section[1] == "UGL":
            result["lib"] = "UGL"
        elif section[1] == "Main Library":
            result["lib"] = "MainLib"
        elif section[1] == "Chemistry Library":
            result["lib"] = "Chem"
        elif section[1] == "ACES Library":
            result["lib"] = "Aces"

        result["conf"] = round(100*spot_confidences[section], 2)
        result["floor"] = section[2]
        result["section"] = section[3]
        result["dist"] = library_df[library_df['libName'] == section[1]].iloc[0]['Distance Words']
        # TODO make sure this is the correct rank based on what ever alg'm we use
        result["rank"] = str(count)
        if environment == "Quiet Open Study" or environment == "Quiet Closed Study":
            result["quiet"] = False
        else:
            result["quiet"] = True
        result["link"] = library_df[library_df['libName'] == section[1]].iloc[0]['reservationLink']
        allResults[res + str(count)] = result
        count+=1

    print(allResults)
    pass_data = {
        "logged_in" : logged_in,
        "allResults": allResults
    }

    # I would say to try to get 5 Max reccomendations to display.
    return render(request, "results/results.html", pass_data)

def update_view(request, *args, **kwargs):
    global logged_in
    if(request.method == "POST"):
        if("UpdatedAddress" in request.POST): # coming from updated address
            updatedAddress = request.POST["UpdatedAddress"]
            student_username = logged_in["username"]
            update_query = 'UPDATE pages_Student SET "mainAddress" = %s WHERE "username" = %s;'
            with connection.cursor() as cursor:
                cursor.execute(update_query, (updatedAddress, student_username))
            default_address = updatedAddress
            # TODO update student's address with student_username
            return render(request, "search/search.html", {"logged_in":logged_in, "default_address":default_address})
        if("Library" in request.POST):
            if(request.POST["Library"] == "update"):
                libName =  request.POST["libName"]
                libraryDept = request.POST["libraryDept"]
                numFloors = request.POST["numFloors"]
                libAddress = request.POST["libAddress"]
                reservationLink = request.POST["reservationLink"]
                update_query = 'UPDATE pages_library SET "libraryDept" = %s, "numFloors" = %s, "libAddress" = %s, "reservationLink" = %s WHERE "libName" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(update_query, (libraryDept, numFloors, libAddress, reservationLink, libName))
                # TODO: update record with primary key libName with the above info
            elif(request.POST["Library"] == "delete"):
                libName =  request.POST["libName"]
                delete_query = 'DELETE FROM pages_library WHERE "libName" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(delete_query, (libName,))
                # TODO: Delete library with name (the primary key) "request.POST["libName"]"
            else:
                libName =  request.POST["libName"]
                libraryDept = request.POST["libraryDept"]
                numFloors = request.POST["numFloors"]
                libAddress = request.POST["libAddress"]
                reservationLink = request.POST["reservationLink"]
                insert_query = 'INSERT INTO pages_library ("libName", "libraryDept", "numFloors", "libAddress", "reservationLink") VALUES (%s, %s, %s, %s, %s);'
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (libName, libraryDept, numFloors, libAddress, reservationLink))
                # TODO: Check that entries are valid and add new Library to the database


        elif("Floor" in request.POST):
            if(request.POST["Floor"] == "update"):
                libName =  request.POST["libName"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                numSeats = request.POST["numSeats"]
                studyEnv = request.POST["studyEnv"]
                update_query = 'UPDATE pages_FloorSection SET "numSeats" = %s, "studyEnv" = %s WHERE "libName" = %s and "floorNum" = %s and "section" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(update_query, (numSeats, studyEnv, libName, floorNum, section))

                # TODO: update record FloorSection with primary key {libName, floornum, and section} with the above info
            elif(request.POST["Floor"] == "delete"):
                libName =  request.POST["libName"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                delete_query = 'DELETE FROM pages_FloorSection WHERE "libName" = %s and "floorNum" = %s and "section" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(delete_query, (libName, floorNum, section))
                # TODO: Delete FloorSection with primary key {libName, floornum, and section}
            else:
                libName =  request.POST["libName"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                numSeats = request.POST["numSeats"]
                studyEnv = request.POST["studyEnv"]
                insert_query = 'INSERT INTO pages_FloorSection ("libName", "floorNum", "section", "numSeats", "studyEnv") VALUES (%s, %s, %s, %s, %s);'
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (libName, floorNum, section, numSeats, studyEnv))
                # TODO: Check that entries are valid and add new FloorSection to the database

        elif("Hours" in request.POST):
            if(request.POST["Hours"] == "update"):
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                openTime = request.POST["openTime"]
                closeTime = request.POST["closeTime"]
                update_query = 'UPDATE pages_hoursofop SET "openTime" = %s, "closeTime" = %s WHERE "libName" = %s and "dayOfWeek" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(update_query, (openTime, closeTime, libName, dayOfWeek))
                # TODO: update record hours of operation with primary key {libName, dayOfWeek} with the above info
            elif(request.POST["Hours"] == "delete"):
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                delete_query = 'DELETE FROM pages_hoursofop WHERE "libName" = %s and "dayOfWeek" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(delete_query, (libName, dayOfWeek))
                # TODO: Delete hours of operation with primary key {libName, dayOfWeek}
            else:
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                openTime = request.POST["openTime"]
                closeTime = request.POST["closeTime"]
                insert_query = 'INSERT INTO pages_hoursofop ("libName", "dayOfWeek", "openTime", "closeTime") VALUES (%s, %s, %s, %s);'
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (libName, dayOfWeek, openTime, closeTime))
                # TODO: Check that entries are valid and add new hours of operation to the database

        elif("Records" in request.POST):
            if(request.POST["Records"] == "update"):
                recordID =  request.POST["recordID"]
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                time = request.POST["time"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                count = request.POST["count"]
                # TODO: update record of Records table with primary key "recordID" with the above info
            elif(request.POST["Records"] == "delete"):
                recordID =  request.POST["recordID"]
                # TODO: Delete Records entry with primary key "recordID"
            else:
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                time = request.POST["time"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                count = request.POST["count"]
                # TODO: Check that entries are valid and add new Records entry to the database, and create a recordID for it.



    # TODO: check if user is a admin and has access
    is_admin = False
    #get username for logged in individual
    try:
        curr_user = Student.objects.raw('SELECT * FROM pages_Student WHERE "username" = %s', [logged_in["username"]])
        if len(curr_user) != 0:
            curr_user = curr_user[0]
            is_admin = curr_user.isAdmin
        else:
            default_address = ""
            isAdmin = False

    except ObjectDoesNotExist:
        is_admin = False

    if(is_admin):
        # TODO: fill library data with actual database info from the "Library" model. Take out dummy
        # data when you are done.
        library_data = {}
        lib_vals = Library.objects.values()
        for lib in lib_vals:
            library_data[lib['libName']] = lib

        # TODO Fill Floor data from database. NOTE: The names should be libname#. Has to do with sorting.
        floor_data = {}
        floor_section_vals = FloorSection.objects.values()
        section_counts = {}
        for floor_section in floor_section_vals:
            if floor_section["libName"] not in section_counts:
                section_counts[floor_section["libName"]] = 1
            key = floor_section['libName'] + str(floor_section['floorNum']) + str(section_counts[floor_section["libName"]])
            floor_data[key] = floor_section
            section_counts[floor_section["libName"]]+=1

        # TODO Fill Hours of Operation data from database. The names should be libname#. Has to do with sorting.
        #1 = Sunday, 7 = Saturday
        hours_data = {}
        hoursOfOp_vals = hoursOfOp.objects.values()
        for hour in hoursOfOp_vals:
            key = hour['libName'] + str(hour['dayOfWeek'])
            hours_data[key] = hour
        # TODO Fill record data from database. The names should be libname#. Has to do with sorting.

        pass_data = {
            "logged_in": logged_in,
            "library_data" : library_data,
            "floor_data": floor_data,
            "hoursOfOp": hours_data,
        }
        return render(request, "update/update.html", pass_data)
    else: # not allowed to be here!
        return render(request, "search/search.html", {"logged_in":logged_in})
