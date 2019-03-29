from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from .models import Student, Library, Request, FloorSection
import pandas as pd
import googlemaps
import requests
from itertools import tee
from django.db import connection


API_key = 'AIzaSyBzozWYI3q9hIHEOh1arRxsMLLzYx83MLQ'
GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

# Create your views here.
def login_view(request, *args, **kwargs):
    logged_in = {"isLoggedIn":False} # pass to html for navbar
    return render(request, "login/login.html", logged_in)


def signup_view(request, *args, **kwargs):
    logged_in = {"isLoggedIn":False} # pass to html for navbar
    return render(request, "signup/signup.html", logged_in)


def search_view(request, *args, **kwargs):
    # check if we are requesting from login or annonomous user.
    if(request.method == "POST"): # post are from login

        # check if request is from a user signup or login
        signup_request = "location" in request.POST # this is only a field in the signup form
        print("here")
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
                return  render(request, "search/search.html", logged_in)
            else: # signup fields are not valid
                logged_in = {"isLoggedIn":False} # pass to html for navbar
                return render(request, "login/login.html", logged_in)

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
                return  render(request, "search/search.html", logged_in)
            else: # user is not valid
                logged_in = {"isLoggedIn":False} # pass to html for navbar
                return render(request, "login/login.html", logged_in)

    else: # get from anon user
        logged_in = {"isLoggedIn":False} # pass to html for navbar
        return render(request, "search/search.html", logged_in)


def results_view(request, *args, **kwargs):
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

    results = {
        "isLoggedIn" : False,
        "allResults": allResults
    }

    # I would say to try to get 5 Max reccomendations to display.

    logged_in = {"isLoggedIn":False} # pass to html for navbar
    return render(request, "results/results.html", results)

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



    # TODO: fill library data with actual database info from the "Library" model. Take out dummy
    # data when you are done.
    library_data = {}
    lib_vals = Library.objects.values()
    for lib in lib_vals:
        library_data[lib['libName']] = lib
    print(library_data)

    pass_data = {
        "isLoggedIn": False,
        "library_data" : library_data
    }
    return render(request, "update/update.html", pass_data)
