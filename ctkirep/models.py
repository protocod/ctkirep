from urllib import response
from django.db import models
from datetime import date

#==============================================================================================================
class CourseType(models.Model):
    name = models.CharField("Course type", max_length=10)
    sorder = models.SmallIntegerField("Order", default=0)
    remote = models.BooleanField(verbose_name="Remote course", default=False)

class CourseSubject(models.Model):
    code = models.CharField("Subject code", max_length=10,unique=True)
    fname = models.CharField("Subject name", max_length=100)

class Course(models.Model):
    type = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    subject_order = models.SmallIntegerField("Subject order", default=0)
    subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE, verbose_name="Subject ID")
    ractivity = models.ForeignKey('ReadingActivity', on_delete=models.PROTECT, verbose_name="Reading activity ID")
    reqtime = models.DurationField(verbose_name="Required reading time", null=True)

#==============================================================================================================
class Student(models.Model):
    name = models.CharField("Name", max_length=30)
    surname = models.CharField("Surname", max_length=30)
    email_addr = models.CharField("E-mail", max_length=50)
    reading_username = models.CharField("iMRS login", max_length=30, unique=True, default='')
    pt_username = models.CharField("ACE login", max_length=30, unique=True, default='')
    course = models.ForeignKey(CourseType, on_delete=models.PROTECT, verbose_name="Course ID")
    start_date = models.DateField(verbose_name="Course start date", default=date.today)

#==============================================================================================================
class ReadingActivity(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField("Reading activity", max_length=50, blank=False, unique=True)

class ReadingTime(models.Model):
    id = models.BigIntegerField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Student user ID")
    activity = models.ForeignKey(ReadingActivity, on_delete=models.CASCADE, verbose_name="Activity ID")
    start = models.DateTimeField(verbose_name="Start time")
    end = models.DateTimeField(verbose_name="End time")
    duration = models.DurationField(verbose_name="Reading duration")

class ReadingTimeUpload(models.Model):
    timestamp = models.DateTimeField()
    file = models.FileField()

    def save(self, *args, **kwargs):
        self.file.name = self.timestamp.strftime('%Y%m%d%H%M%S_') + self.file.name
        super().save(*args, **kwargs)

#==============================================================================================================
class ACEActivityType(models.Model):
    name = models.CharField(max_length=25)

class ACEActivity(models.Model):
    link = models.CharField(max_length=200)
    extref = models.CharField(max_length=200)
    name = models.CharField(max_length=100, verbose_name="Activity name")
    atype = models.ForeignKey(ACEActivityType, on_delete=models.CASCADE, verbose_name="Display type")
    subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE, verbose_name="Subject ID")
    ord = models.SmallIntegerField()
    
class ACEStatus(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=20)

class ACEContentStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Student")
    timestamp = models.DateTimeField(null=True, verbose_name="Timestamp")
    activity = models.ForeignKey(ACEActivity, on_delete=models.CASCADE, verbose_name="Activity") 
    status = models.ForeignKey(ACEStatus, on_delete=models.CASCADE, verbose_name="Status")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score', null=True)

class ACELearnerJourney(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Student")
    timestamp = models.DateTimeField(verbose_name="Timestamp")
    attempt = models.SmallIntegerField(verbose_name='Attempt')
    duration = models.DurationField(verbose_name="Reading duration", null=True)
    activity = models.ForeignKey(ACEActivity, on_delete=models.CASCADE, verbose_name="Activity")
    action = models.ForeignKey(ACEStatus, on_delete=models.CASCADE, verbose_name="Action")
    response = models.TextField()
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score', null=True)

class PTUpload(models.Model):
    timestamp = models.DateTimeField()
    file = models.FileField()

    def save(self, *args, **kwargs):
        self.file.name = self.timestamp.strftime('%Y%m%d%H%M%S_') + self.file.name
        super().save(*args, **kwargs)