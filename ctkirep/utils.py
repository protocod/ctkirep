from os import stat
import xml.etree.ElementTree as ET
import csv, time
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

from ctkirep.models import ReadingActivity, ReadingTime, Student, ACEContentStatus, ACEActivity, ACEStatus, ACEActivityType, ACELearnerJourney

def bulk_reading_time(xml_path):
    try:
        xml_tree = ET.parse(xml_path)
    except ET.ParseError:
        return 'Invalid XML file: ' + xml_path

    root = xml_tree.getroot()
    trk = root.find('tracking')
    if trk is None:
        return 'Invalid XML file: ' + xml_path

    ReadingTime.objects.all().delete()
    new_id = 1
    new_data = list()
    for res in trk.findall('result'):
        ident = res.find('identifier').text
        xactivity = res.find('activity').text
        rtime = res.find('revisiontime').text
        stime = res.find('starttime').text
        if stime is None:
            stime = ""
        etime = res.find('endtime').text
        if etime is None:
            etime = stime

        dt1 = datetime.strptime(stime, '%d/%m/%Y %H:%M:%S')
        dt2 = datetime.strptime(etime, '%d/%m/%Y %H:%M:%S')

        try:
            st = Student.objects.get(reading_username=ident)
        except ObjectDoesNotExist:
            return 'Username [' + ident + '] not valid'
        try:
            ra = ReadingActivity.objects.get(name=xactivity)
        except ObjectDoesNotExist:
            return 'Reading activity [' + xactivity + '] not valid'

        new_data.append(ReadingTime(student=st, activity=ra, start=dt1, end=dt2, duration=(dt2-dt1), id=new_id))
        new_id += 1

    ReadingTime.objects.bulk_create(new_data, len(new_data))
    
    return 'OK'

def ace_contentstatus(csv_path):
    if not csv_path:
        return "Empty CSV file path"

    try:
        csv_file = open(csv_path, newline='')
    except OSError as osErr:
        return osErr.strerror()
    
    schema1 = ['\ufeffUsername','First name','Surname','Groups','Timestamp','Date','Time','Activity ID','Activity external reference','Activity name','Display type','Status','Score','CPD points','Learning hours']
    schema2 = ['Username','First name','Surname','Groups','Timestamp','Date','Time','Activity ID','Activity external reference','Activity name','Display type','Status','Score','CPD points','Learning hours']
    try:
        csvrdr = csv.DictReader(csv_file)
        if schema1 != csvrdr.fieldnames:
            if schema2 != csvrdr.fieldnames:
                return "File is not ContentStatus report"
            else:
                usercol = 'Username'
        else:
            usercol = '\ufeffUsername'

        for row in csvrdr:            
            try:
                st = Student.objects.get(pt_username=row[usercol].strip())
            except ObjectDoesNotExist:
                return 'Username [' + row[usercol] + '] not valid'
            
            #Timestamp
            ts = None
            if row['Timestamp'] != '-':
                ts = datetime.strptime(row['Timestamp'].strip(), '%Y-%m-%dT%H:%M:%S.%fZ')

            #Activity
            try:
                ate = ACEActivityType.objects.get(name=row['Display type'].strip())
            except ObjectDoesNotExist:
                return 'Unknown activity type: ' + row['Display type']

            try:
                act = ACEActivity.objects.get(name=row['Activity name'].strip())
            except ObjectDoesNotExist:
                return 'Unknown activity: ' + row['Activity name']

            try:
                stat = ACEStatus.objects.get(name=row['Status'].strip())
            except ObjectDoesNotExist:
                return 'Unknown activity: ' + row['Status']

            scr = None
            if row['Score'].strip() != '-':
                scr = row['Score']

            ACEContentStatus.objects.update_or_create(student=st, activity=act, defaults={'timestamp':ts, 'status':stat, 'score':scr})

    except csv.Error as csvErr:
        return 'file {}, line {}: {}'.format(csv_path, csvrdr.line_num, csvErr)

    csv_file.close()
    return 'OK'

def ace_journeyreport(csv_path):
    if not csv_path:
        return "Empty CSV file path"

    try:
        csv_file = open(csv_path, newline='')
    except OSError as osErr:
        return osErr.strerror()

    schema1 = ['\ufeffUsername', 'First name', 'Surname', 'Groups', 'Timestamp', 'Date', 'Time', 'Attempt', 'Duration', 'Statement ID', 'Course ID', 'Course', 'Activity ID', 'Activity name', 'Type', 'Action', 'Response', 'Mark', 'Score']
    schema2 = ['Username', 'First name', 'Surname', 'Groups', 'Timestamp', 'Date', 'Time', 'Attempt', 'Duration', 'Statement ID', 'Course ID', 'Course', 'Activity ID', 'Activity name', 'Type', 'Action', 'Response', 'Mark', 'Score']

    try:
        csvrdr = csv.DictReader(csv_file)
        if schema1 != csvrdr.fieldnames:
            if schema2 != csvrdr.fieldnames:
                return "File is not ContentStatus report"
            else:
                usercol = 'Username'
        else:
            usercol = '\ufeffUsername'

        time_check = dict()
        last_time = ACELearnerJourney.objects.values('student__pt_username').annotate(maxts=Max('timestamp'))
        for lt in last_time:
            time_check[lt['student__pt_username']] = lt['maxts']

        new_data = list()
        for row in csvrdr:
            if (len(row['Action'])) == 0:
                continue
            
            #Check if this record is new
            lastts = time_check.get(row[usercol].strip())
   
            #Timestamp
            ts = datetime.strptime(row['Timestamp'].strip(), '%Y-%m-%dT%H:%M:%S.%fZ')

            if (lastts) and (ts <= lastts):
                continue

            #Student
            try:
                st = Student.objects.get(pt_username=row[usercol].strip())
            except ObjectDoesNotExist:
                return 'Username [' + row[usercol] + '] not valid'

            #Attempt
            atmpt = int(row['Attempt'].strip())

            #Duration
            dr = None
            if len(row['Duration']):
                times = time.strptime(row['Duration'].replace('PT',''), '%HH%MM%SS')
                dr = timedelta(hours=times.tm_hour, minutes=times.tm_min, seconds=times.tm_sec)

            #Activity type
            try:
                activity_type = ACEActivityType.objects.get(name=row['Type'].strip())
            except ObjectDoesNotExist:
                return 'Unknown activity type: ' + row['Type']

            #Activity
            try:
                act = ACEActivity.objects.get(name=row['Course'].strip())
            except ObjectDoesNotExist:
                return 'Unknown activity: ' + row['Course']

            #Action
            try:
                stat = ACEStatus.objects.get(name=row['Action'].strip())
            except ObjectDoesNotExist:
                return 'Unknown activity status: ' + row['Action']

            #Response
            resp = row['Response']

            #Score
            scr = None
            if row['Score'].strip() != '-':
                scr = row['Score']

            new_data.append(ACELearnerJourney(student=st, timestamp=ts, attempt=atmpt, duration=dr, activity=act, action=stat, response=resp, score=scr))

        if len(new_data):
            ACELearnerJourney.objects.bulk_create(new_data, len(new_data))

    except csv.Error as csvErr:
        return 'file {}, line {}: {}'.format(csv_path, csvrdr.line_num, csvErr)

    csv_file.close()
    return 'OK, {0} rows inserted'.format(len(new_data))