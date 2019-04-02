from django.db import models
import uuid
from datetime import datetime
# Create your models here.

class Student(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    passwordHash = models.CharField(max_length=255)
    prefStudyEnv = models.CharField(max_length=255)
    mainAddress = models.CharField(max_length=255)
    favLibrary = models.CharField(max_length=255)
    major = models.CharField(max_length=255)

class Request(models.Model):
    requestID = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)

class Library(models.Model):
    libName = models.CharField(max_length=255, primary_key=True)
    libraryDept = models.CharField(max_length=255)
    numFloors = models.IntegerField(default=0)
    libAddress = models.CharField(max_length=255)
    reservationLink = models.CharField(max_length=255)

class FloorSection(models.Model):
    libName = models.CharField(max_length=255)
    floorNum = models.IntegerField(default=0)
    section = models.CharField(max_length=255)
    numSeats = models.IntegerField(default=0)
    studyEnv = models.CharField(max_length=255)

    class Meta:
        unique_together = (('libName', 'floorNum', 'section'),)

class hoursOfOp(models.Model):
    libName = models.CharField(max_length=255)
    dayOfWeek = models.IntegerField()
    openTime = models.IntegerField()
    closeTime = models.IntegerField()

    class Meta:
        unique_together = (('libName', 'dayOfWeek'),)

class recordData(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True, primary_key=True)
    count = models.IntegerField()

                    # "libName" : "Grainger",
                    # "floorNum" : 2,
                    # "section" : "2_A",
                    # "count" : 25,
                    # "dayOfWeek": 0,
                    # "time": 12

class specialDateRanges(models.Model):
    eventName = models.CharField(max_length=255)
    dateTimeStart = models.DateTimeField(default=datetime.now(), blank=False)
    dateTimeEnd = models.DateTimeField(default=datetime.now(), blank=False)
