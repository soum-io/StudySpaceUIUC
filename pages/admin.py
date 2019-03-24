from django.contrib import admin
from .models import Student, Request, Library, FloorSection, hoursOfOp, recordData, specialDateRanges

# Register your models here.

admin.site.register(Student)
admin.site.register(Request)
admin.site.register(Library)
admin.site.register(FloorSection)
admin.site.register(hoursOfOp)
admin.site.register(recordData)
admin.site.register(specialDateRanges)
