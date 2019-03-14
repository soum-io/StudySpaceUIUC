from django.http import HttpResponse
from django.shortcuts import render


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
    enviroment = request.GET["enviroment"] # will either be "Quiet Open Study", "Quiet Closed Study", or "Group Study"

    # TODO: Use search information to get reccomendations. Each reccomendation need to contain the following information:
    # 1. library abbreviation (e.g. "UGL")
    # 2. Floor (e.g. "4F" for fourth floor)
    # 3. Floor Section (Like left or right or however else we store it)
    # 4. How far the library is from the location the user entered (e.g. "20M" for 20 miles)
    # 5. Boolean if the section is quiet or not
    # 6. How confident we are. (e.g. "70%" or "50%")

    # I would say to try to get 5 Max reccomendations to display.


    logged_in = {"isLoggedIn":False} # pass to html for navbar
    return render(request, "results/results.html", logged_in)
