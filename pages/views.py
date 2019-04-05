from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from .models import Student, Library, Request, FloorSection
import pandas as pd
import googlemaps
import requests
from itertools import tee
from django.db import connection

# how to pass to page to page if user is logged in or not. This is really bad
# for privacy as there is much more secure ways to do this. If there is time
# before the final presentation, this will be fixed
logged_in = {"isLoggedIn": False, "username": ""}

API_key = 'AIzaSyBzozWYI3q9hIHEOh1arRxsMLLzYx83MLQ'
GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

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
        if(signup_request): # coming from signup

            # get singup form data
            email = request.POST["email"]
            location = request.POST["location"]
            password = request.POST["password"]
            passwordAgain = request.POST["passwordAgain"]

            # TODO: Check that the provided signup information sufficient. If so, add user to the database
            valid_signup = False
            if password == passwordAgain:
                passHash = make_password(password)
                #new_user = Student(username=email, passwordHash=passHash, mainAddress=location)
                #new_user.save()
                insert_query = 'INSERT INTO pages_student ("username", "passwordHash", "mainAddress", "prefStudyEnv", "favLibrary", "major") VALUES (%s, %s, %s, \'\', \'\', \'\');'
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (email, passHash, location))
                print("Student Registered")
                valid_signup = True

            if(valid_signup): # user is created now redirect to search
                logged_in = {"isLoggedIn":True, "username":email} # pass to html for navbar
                return  render(request, "search/search.html", {"logged_in":logged_in})
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
            temp_student = Student.objects.get(username=email)
            print("student", temp_student)
            if check_password(password, temp_student.passwordHash):
                print("Success Match")
                matches = True

            if(matches): # if user if valid
                logged_in = {"isLoggedIn":True, "username":email} # pass to html for navbar
                return  render(request, "search/search.html", {"logged_in":logged_in})
            else: # user is not valid
                logged_in = {"isLoggedIn":False, "username": ""} # pass to html for navbar
                return render(request, "login/login.html", {"logged_in":logged_in})

    else: # get from anon or entering another search from results page user
        return render(request, "search/search.html", {"logged_in":logged_in})

def results_view(request, *args, **kwargs):
    global logged_in
    print(request.GET)
    # get search form data
    location = request.GET["location"] # address as string address, not coordinates
    groupSize = request.GET["groupSize"] # will be a digit in string format
    forDate = request.GET["forDate"] # format is "mm/dd/yyyy"
    forTime = request.GET["forTime"] # format is "01:00 AM"
    environment = request.GET["enviroment"] # will either be "Quiet Open Study", "Quiet Closed Study", or "Group Study"

    # TODO: Use search information to get reccomendations. Each reccomendation need to contain the following information:
    # 1. library abbreviation (e.g. "UGL"). only "UGL", "GG", and "MainLib" are supported right now.
    # 2. Floor (e.g. "4F" for fourth floor)
    # 3. Floor Section (Like left or right or however else we store it)
    # 4. How far the library is from the location the user entered (e.g. "20M" for 20 miles)
    # 5. Boolean if the section is quiet or not
    # 6. How confident we are. (e.g. "70" or "50", should be as a percentage)

    # put the recommendations in the following dictionary allResults. When ready, remove the two
    # results in their with the number of results the algorithm returns.

    library_df = pd.DataFrame(list(Library.objects.all().values('libName', 'libAddress', 'reservationLink')))
    #comment these out once all libraries are supported

    gmaps = googlemaps.Client(key=API_key)
    origins = []
    origins.append(location)
    destinations = list(library_df['libAddress'])
    matrix = gmaps.distance_matrix(location, destinations, mode="walking", units="imperial")
    elems = matrix["rows"][0]["elements"]
    distances = []
    for dist in elems:
        lib_distance = dist["distance"]['text']
        distances.append(lib_distance)
    library_df['Distance'] = distances

    section_df = pd.DataFrame()
    if environment == "Group Study":
        section_df = pd.DataFrame(list(FloorSection.objects.filter(studyEnv="collaborative").values()))
    elif environment == "Quiet Open Study":
        section_df = pd.DataFrame(list(FloorSection.objects.filter(studyEnv="quiet").values()))
    elif environment == "Quiet Closed Study":
        section_df = pd.DataFrame(list(FloorSection.objects.filter(studyEnv="quiet").values()))
    else:
        section_df = pd.DataFrame(list(FloorSection.objects.filter(studyEnv="EWS").values()))

    allResults = {}
    res = "result"
    count = 1
    for index, section in section_df.iterrows():
        result = {}
        if section['libName'] == "Grainger":
            result["lib"] = "GG"
            result["conf"] = "75"
        elif section['libName'] == "UGL":
            result["lib"] = "UGL"
            result["conf"] = "50"
        elif section['libName'] == "Main Library":
            result["lib"] = "MainLib"
            result["conf"] = "25"
        result["floor"] = section['floorNum']
        result["section"] = section['section']
        result["dist"] = library_df[library_df['libName'] == section['libName']].iloc[0]['Distance']
        if environment == "Quiet Open Study" or environment == "Quiet Closed Study":
            result["quiet"] = True
        else:
            result["quiet"] = False
        result["link"] = library_df[library_df['libName'] == section['libName']].iloc[0]['reservationLink']
        allResults[res + str(count)] = result
        count+=1

    pass_data = {
        "logged_in" : logged_in,
        "allResults": allResults
    }

    # I would say to try to get 5 Max reccomendations to display.
    return render(request, "results/results.html", pass_data)

def update_view(request, *args, **kwargs):
    if(request.method == "POST"):
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
                delete_query = 'DELETE FROM pages_FloorSection WHERE "libname" = %s and "floorNum" = %s and "section" = %s;'
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
                update_query = 'UPDATE pages_hours SET "openTime" = %s, "closeTime" = %s WHERE "libName" = %s and "dayOfWeek" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(update_query, (openTime, closeTime, libName, dayOfWeek))
                # TODO: update record hours of operation with primary key {libName, dayOfWeek} with the above info
            elif(request.POST["Hours"] == "delete"):
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                delete_query = 'DELETE FROM pages_hours WHERE "libname" = %s and "dayOfWeek" = %s;'
                with connection.cursor() as cursor:
                    cursor.execute(delete_query, (libName, dayOfWeek))
                # TODO: Delete hours of operation with primary key {libName, dayOfWeek}
            else:
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                openTime = request.POST["openTime"]
                closeTime = request.POST["closeTime"]
                insert_query = 'INSERT INTO pages_hours ("libName", "dayOfWeek", "openTime", "closeTime") VALUES (%s, %s, %s, %s);'
                with connection.cursor() as cursor:
                    cursor.execute(insert_query, (libName, dayOfWeek, openTime, closeTime))
                # TODO: Check that entries are valid and add new hours of operation to the database

        elif("Records" in request.POST):
            if(request.POST["Records"] == "update"):
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                time = request.POST["time"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                count = request.POST["count"]
                # TODO: update record of Records table with primary key {libName, dayOfWeek, time, floorNum, section} with the above info
            elif(request.POST["Records"] == "delete"):
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                time = request.POST["time"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                # TODO: Delete Records entry with primary key {libName, dayOfWeek, time, floorNum, section}
            else:
                libName =  request.POST["libName"]
                dayOfWeek = request.POST["dayOfWeek"]
                time = request.POST["time"]
                floorNum = request.POST["floorNum"]
                section = request.POST["section"]
                count = request.POST["count"]
                # TODO: Check that entries are valid and add new Records entry to the database



    # TODO: check if user is a admin and has access
    global logged_in
    is_admin = True
    if(is_admin):
        # TODO: fill library data with actual database info from the "Library" model. Take out dummy
        # data when you are done.
        library_data = {}
        lib_vals = Library.objects.values()
        for lib in lib_vals:
            library_data[lib['libName']] = lib
        print(library_data)

        # TODO Fill Floor data from database. NOTE: The names should be libname#. Has to do with sorting.
        floor_data = {
            "UGL quiet": {
                "libName" : "UGL",
                "floorNum" : 1,
                "section" : "ALL",
                "numSeats" : 760,
                "studyEnv" : "Quiet Open Study"
            },
            "UGL collaborative": {
                "libName" : "UGL",
                "floorNum" : 2,
                "section" : "ALL",
                "numSeats" : 384,
                "studyEnv" : "collaborative"
            },
            "Main Library1": {
                "libName" : "Main Library",
                "floorNum" : 2,
                "section" : "All",
                "numSeats" : 434,
                "studyEnv" : "Quiet Open Study"
            },
            "Main Library1": {
                "libName" : "Main Library",
                "floorNum" : 1,
                "section" : "All",
                "numSeats" : 264,
                "studyEnv" : "Quiet Open Study"
            },
            "Chemistry Library": {
                "libName" : "Chemistry Library",
                "floorNum" : 1,
                "section" : "Noyes",
                "numSeats" : 77,
                "studyEnv" : "Quiet Closed Study"
            },
            "Grainger4West": {
                "libName" : "Grainger",
                "floorNum" : 4,
                "section" : "West",
                "numSeats" : 107,
                "studyEnv" : "collaborative"
            },
            "Grainger4Central": {
                "libName" : "Grainger",
                "floorNum" : 4,
                "section" : "central",
                "numSeats" : 102,
                "studyEnv" : "collaborative"
            },
            "Grainger4EWS": {
                "libName" : "Grainger",
                "floorNum" : 4,
                "section" : "EWS",
                "numSeats" : 100,
                "studyEnv" : "EWS"
            },
            "Grainger4East": {
                "libName" : "Grainger",
                "floorNum" : 4,
                "section" : "East",
                "numSeats" : 32,
                "studyEnv" : "collaborative"
            },
            "Grainger3": {
                "libName" : "Grainger",
                "floorNum" : 3,
                "section" : "ALL",
                "numSeats" : 85,
                "studyEnv" : "Quiet Closed Study"
            },
            "Grainger2": {
                "libName" : "Grainger",
                "floorNum" : 2,
                "section" : "ALL",
                "numSeats" : 557,
                "studyEnv" : "Quiet Closed Study"
            },
            "Grainger1W": {
                "libName" : "Grainger",
                "floorNum" : 1,
                "section" : "West",
                "numSeats" : 0,
                "studyEnv" : "Group Study"
            },
            "Grainger1EWS": {
                "libName" : "Grainger",
                "floorNum" : 1,
                "section" : "EWS",
                "numSeats" : 0,
                "studyEnv" : "EWS"
            }
        }

        # TODO Fill Hours of Operation data from database. The names should be libname#. Has to do with sorting.
        #0 = Sunday, 6 = Saturday
        hoursOfOp = {
            "Grainger6": {
                "libName" : "Grainger",
                "dayOfWeek" : 6,
                "openTime": 0,
                "closeTime": 2400
            },
            "Grainger5": {
                "libName" : "Grainger",
                "dayOfWeek" : 5,
                "openTime": 0,
                "closeTime": 2400
            },
            "Grainger4": {
                "libName" : "Grainger",
                "dayOfWeek" : 4,
                "openTime": 0,
                "closeTime": 2400
            },
            "Grainger3": {
                "libName" : "Grainger",
                "dayOfWeek" : 3,
                "openTime": 0,
                "closeTime": 2400
            },
            "Grainger2": {
                "libName" : "Grainger",
                "dayOfWeek" : 2,
                "openTime": 0,
                "closeTime": 2400
            },
            "Grainger1": {
                "libName" : "Grainger",
                "dayOfWeek" : 1,
                "openTime": 0,
                "closeTime": 2400
            },
            "Grainger0": {
                "libName" : "Grainger",
                "dayOfWeek" : 0,
                "openTime": 0,
                "closeTime": 2400
            },
            "Chem6": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 6,
                "openTime": 1300,
                "closeTime": 1700
            },
            "Chem5": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 5,
                "openTime": 900,
                "closeTime": 1700
            },
            "Chem4": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 4,
                "openTime": 900,
                "closeTime": 2200
            },
            "Chem3": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 3,
                "openTime": 900,
                "closeTime": 2200
            },
            "Chem2": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 2,
                "openTime": 900,
                "closeTime": 1700
            },
            "Chem1": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 1,
                "openTime": 900,
                "closeTime": 1700
            },
            "Chem0": {
                "libName" : "Chemistry Library",
                "dayOfWeek" : 0,
                "openTime": 1300,
                "closeTime": 2200
            },
            "Main6": {
                "libName" : "Main Library",
                "dayOfWeek" : 6,
                "openTime": 0,
                "closeTime": 0
            },
            "Main5": {
                "libName" : "Main Library",
                "dayOfWeek" : 5,
                "openTime": 850,
                "closeTime": 1800
            },
            "Main4": {
                "libName" : "Main Library",
                "dayOfWeek" : 4,
                "openTime": 850,
                "closeTime": 2200
            },
            "Main3": {
                "libName" : "Main Library",
                "dayOfWeek" : 3,
                "openTime": 850,
                "closeTime": 2200
            },
            "Main2": {
                "libName" : "Main Library",
                "dayOfWeek" : 2,
                "openTime": 850,
                "closeTime": 1700
            },
            "Main1": {
                "libName" : "Main Library",
                "dayOfWeek" : 1,
                "openTime": 850,
                "closeTime": 1700
            },
            "Main0": {
                "libName" : "Main Library",
                "dayOfWeek" : 0,
                "openTime": 0,
                "closeTime": 0
            },
            "UGL6": {
                "libName" : "UGL",
                "dayOfWeek" : 6,
                "openTime": 0,
                "closeTime": 0
            },
            "UGL5": {
                "libName" : "UGL",
                "dayOfWeek" : 5,
                "openTime": 750,
                "closeTime": 1900
            },
            "UGL4": {
                "libName" : "UGL",
                "dayOfWeek" : 4,
                "openTime": 750,
                "closeTime": 1450
            },
            "UGL3": {
                "libName" : "UGL",
                "dayOfWeek" : 3,
                "openTime": 750,
                "closeTime": 1450
            },
            "UGL2": {
                "libName" : "UGL",
                "dayOfWeek" : 2,
                "openTime": 850,
                "closeTime": 1700
            },
            "UGL1": {
                "libName" : "UGL",
                "dayOfWeek" : 1,
                "openTime": 850,
                "closeTime": 1700
            },
            "UGL0": {
                "libName" : "UGL",
                "dayOfWeek" : 0,
                "openTime": 0,
                "closeTime": 0
            },
            "ACES6": {
                "libName" : "ACES Library",
                "dayOfWeek" : 6,
                "openTime": 0,
                "closeTime": 0
            },
            "ACES5": {
                "libName" : "ACES Library",
                "dayOfWeek" : 5,
                "openTime": 850,
                "closeTime": 1900
            },
            "ACES4": {
                "libName" : "ACES Library",
                "dayOfWeek" : 4,
                "openTime": 850,
                "closeTime": 1450
            },
            "ACES3": {
                "libName" : "ACES Library",
                "dayOfWeek" : 3,
                "openTime": 850,
                "closeTime": 1450
            },
            "ACES2": {
                "libName" : "ACES Library",
                "dayOfWeek" : 2,
                "openTime": 850,
                "closeTime": 1700
            },
            "ACES1": {
                "libName" : "ACES Library",
                "dayOfWeek" : 1,
                "openTime": 850,
                "closeTime": 1700
            },
            "ACES0": {
                "libName" : "ACES Library",
                "dayOfWeek" : 0,
                "openTime": 0,
                "closeTime": 0
            }
        }

        # TODO Fill record data from database. The names should be libname#. Has to do with sorting.
        record_data = {
            "grainger0": {
                "libName" : "Grainger",
                "floorNum" : 2,
                "section" : "2_A",
                "count" : 25,
                "dayOfWeek": 0,
                "time": 12
            },
            "grainger1": {
                "libName" : "Grainger",
                "floorNum" : 2,
                "section" : "2_A",
                "count" : 30,
                "dayOfWeek": 3,
                "time": 12
            }
        }

        pass_data = {
            "logged_in": logged_in,
            "library_data" : library_data,
            "floor_data": floor_data,
            "hoursOfOp": hoursOfOp,
            "record_data" : record_data
        }
        return render(request, "update/update.html", pass_data)
    else: # not allowed to be here!
        return render(request, "search/search.html", {"logged_in":logged_in})
