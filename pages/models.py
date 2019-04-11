from django.db import models
import uuid
from datetime import datetime
from django.utils import timezone
# Create your models here.

class Student(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    passwordHash = models.CharField(max_length=255)
    prefStudyEnv = models.CharField(max_length=255)
    mainAddress = models.CharField(max_length=255)
    favLibrary = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    isAdmin = models.BooleanField(default=False)

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
    recordID = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    entryTime = models.DateTimeField(default=timezone.now, blank=False)
    libName = models.CharField(max_length=255)
    floorNum = models.IntegerField(default=0)
    section = models.CharField(max_length=255)
    dayOfWeek = models.IntegerField()
    time = models.IntegerField()
    count = models.IntegerField(default=0)

class specialDateRanges(models.Model):
    eventName = models.CharField(max_length=255)
    dateTimeStart = models.DateTimeField(default=timezone.now, blank=False)
    dateTimeEnd = models.DateTimeField(default=timezone.now, blank=False)
