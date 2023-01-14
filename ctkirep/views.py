import csv
from datetime import timedelta, date
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Sum, F, OuterRef, Subquery, Max, Count, Q, DateField, ExpressionWrapper

from ctkirep.forms import UploadFileForm, PTFileForm, RTExportForm
from ctkirep.utils import bulk_reading_time, ace_contentstatus, ace_journeyreport
from ctkirep.models import ReadingTime, CourseType, Student, Course, ACEContentStatus, ACELearnerJourney
from ctkirep.templatetags.ctkirep_extras import duration, diffduration

# Login
# ========================================================================
class CTKIRepLoginView(LoginView):
    template = 'ctkirep/login.html'

class CTKIRepPassChangeView(PasswordChangeView):
    template_name = 'ctkirep/change_password.html'
    success_url = reverse_lazy('home')

# Reading time
# ========================================================================
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "ctkirep/home.html"

class ReadingHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'ctkirep/reading_time_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_types = CourseType.objects.order_by('sorder')
        context['coursetypes'] = course_types
        return context

class ReadingTimeView(LoginRequiredMixin, TemplateView):
    template_name = "ctkirep/reading_time_report.html"
    students = Student.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = Student.objects.filter(course=self.kwargs['course'], active=True)
        context['students'] = students
        data = dict()
        for student in students:
            rt = ReadingTime.objects.values('student_id', 'activity_id').annotate(totaltime=Sum('duration'), last_time=Max('end'), alert=Count(
                'duration', filter=Q(duration=timedelta(minutes=90)))).filter(student_id=student.id, activity_id=OuterRef('ractivity_id'))
            st_data = Course.objects.filter(type=self.kwargs['course']).values('subject_order', 'subject__id', 'subject__code', 'subject__fname', 'ractivity__name', 'reqtime', 'ractivity_id').annotate(
                totaltime=Subquery(rt.values('totaltime')), last_time=Subquery(rt.values('last_time')), diff=F('totaltime')-F('reqtime'), alert=Subquery(rt.values('alert'))).order_by('subject_order')
            data[student.id] = st_data
        context['data'] = data
        context['coursetypes'] = CourseType.objects.order_by('sorder')
        context['subject_name'] = CourseType.objects.get(
            pk=self.kwargs['course']).name
        return context

class ReadingTimeDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "ctkirep/reading_time_details.html"
    students = Student.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = get_list_or_404(Student, id=self.kwargs['id'])
        data = dict()
        for student in students:
            rt = ReadingTime.objects.values('student_id', 'activity_id').annotate(totaltime=Sum(
                'duration')).filter(student_id=student.id, activity_id=OuterRef('ractivity_id'))
            st_data = Course.objects.filter(type=self.kwargs['course']).values('subject_order', 'subject__id', 'subject__code', 'subject__fname', 'ractivity__name', 'reqtime', 'ractivity_id').annotate(
                totaltime=Subquery(rt.values('totaltime'))).annotate(diff=F('totaltime')-F('reqtime')).order_by('subject_order')
            data[student.id] = st_data
        context['data'] = data
        context['coursetypes'] = CourseType.objects.order_by('sorder')
        context['subject_name'] = CourseType.objects.get(
            pk=self.kwargs['course']).name
        return context

@login_required
def reading_time_upload(request):
    res = ''
    course_types = CourseType.objects.order_by('sorder')
    context = {'coursetypes': course_types, }
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upl_file = form.save(commit=False)
            upl_file.save()
            res = bulk_reading_time(upl_file.file.path)

    form = UploadFileForm(initial={
                          'upload_status': res, 'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")})
    context['form'] = form
    return render(request, 'ctkirep/reading_time_upload.html', context)

@login_required
def reading_time_export(request):
    course_types = CourseType.objects.values('id', 'name').order_by('sorder')
    course_choices = []
    for cd in course_types:
        course_choices.append((cd['id'], cd['name']))

    context = {'coursetypes': course_types, }
    if request.method == 'POST':
        form = RTExportForm(course_choices, request.POST)
        if form.is_valid():
            return csv_export_rt(request, form.cleaned_data['course'], course_types.get(id=form.cleaned_data['course'])['name'], form.cleaned_data['start_date'], form.cleaned_data['end_date'])
    else:
        form = RTExportForm(course_choices)

    context['form'] = form
    return render(request, 'ctkirep/reading_time_export.html', context)

# Progress tests
# ========================================================================
class PTBaseView(LoginRequiredMixin, TemplateView):
    template_name = 'ctkirep/progress_tests_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_types = CourseType.objects.order_by('sorder')
        context['coursetypes'] = course_types
        return context
class PTStatusReportView(PTBaseView):
    template_name = 'ctkirep/progress_tests_report.html'
    students = Student.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = students = Student.objects.filter(course=self.kwargs['course'], active=True)
        data = dict()
        maxatt_q = ACELearnerJourney.objects.values('student', 'activity').annotate(Max(
            'attempt')).filter(student_id=OuterRef('student_id'), activity_id=OuterRef('activity_id'))
        for student in students:
            data[student.id] = ACEContentStatus.objects.filter(activity__subject__course__type=self.kwargs['course'], student_id=student.id).values('activity__subject__course__subject_order', 'activity__subject__code', 'activity__subject__fname', 'student__id', 'activity__name', 'status__name', 'timestamp', 'score').annotate(max_attempt=Subquery(maxatt_q.values('attempt__max'))).order_by('student_id', 'activity__subject__course__subject_order', 'activity__ord')
        context['data'] = data
        context['students'] = students
        context['coursetypes'] = CourseType.objects.order_by('sorder')
        context['subject_name'] = CourseType.objects.get(
            pk=self.kwargs['course']).name
        return context

@login_required
def content_status_upload(request, rtype):
    res = ''
    course_types = CourseType.objects.order_by('sorder')
    context = {'coursetypes': course_types, }
    if request.method == 'POST':
        form = PTFileForm(request.POST, request.FILES)
        if form.is_valid():
            upl_file = form.save(commit=False)
            upl_file.save()
            if rtype == 1:
                res = ace_contentstatus(upl_file.file.path)
            else:
                res = ace_journeyreport(upl_file.file.path)

    form = PTFileForm(initial={
                      'upload_status': res, 'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")})
    context['form'] = form
    if rtype == 1:
        context['label'] = 'Content status upload'
    else:
        context['label'] = 'Student journey upload'

    return render(request, 'ctkirep/progress_tests_upload.html', context)

@login_required
def progress_test_export(request):
    course_types = CourseType.objects.values('id', 'name').order_by('sorder')
    course_choices = []
    for cd in course_types:
        course_choices.append((cd['id'], cd['name']))

    context = {'coursetypes': course_types, }
    if request.method == 'POST':
        form = RTExportForm(course_choices, request.POST)
        if form.is_valid():
            return csv_export_pt(request, form.cleaned_data['course'], course_types.get(id=form.cleaned_data['course'])['name'], form.cleaned_data['start_date'], form.cleaned_data['end_date'])
    else:
        form = RTExportForm(course_choices)

    context['form'] = form
    return render(request, 'ctkirep/reading_time_export.html', context)
# Students
# ========================================================================
class StudentsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'ctkirep/students_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_types = CourseType.objects.order_by('sorder')
        context['coursetypes'] = course_types
        return context

class StudentsTableView(LoginRequiredMixin, TemplateView):
    template_name = "ctkirep/students_table.html"
    students = Student.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students = Student.objects.filter(course=self.kwargs['course']).annotate(
            sub_end=ExpressionWrapper(F('start_date') + 18*30, output_field=DateField()))
        course_types = CourseType.objects.order_by('sorder')
        context['coursetypes'] = course_types
        context['students'] = students
        context['subject_name'] = CourseType.objects.get(
            pk=self.kwargs['course']).name
        return context

# CSV export views
# ========================================================================
@login_required
def csv_export_rt(request, courseid, course_name, start_date, end_date):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="ReadingTime_{0}_{1}_{2}.csv"'.format(course_name, start_date, end_date)},
    )

    writer = csv.writer(response)
    writer.writerow(['Name', 'Surname', 'Code', 'Subject', 'Activity', 'Required time', 'Reading time', 'Difference', 'Last read time', 'Max timer'])
    students = get_list_or_404(Student, course=courseid)
    for student in students:
        rt = ReadingTime.objects.values('student_id', 'activity_id').annotate(totaltime=Sum('duration'), last_time=Max('end'), alert=Count(
            'duration', filter=Q(duration=timedelta(minutes=90)))).filter(student_id=student.id, start__gte=start_date, end__lte=end_date, activity_id=OuterRef('ractivity_id'))
        st_data = Course.objects.filter(type=courseid).values('subject_order', 'subject__id', 'subject__code', 'subject__fname', 'ractivity__name', 'reqtime', 'ractivity_id').annotate(
            totaltime=Subquery(rt.values('totaltime')), last_time=Subquery(rt.values('last_time')), diff=F('totaltime')-F('reqtime'), alert=Subquery(rt.values('alert'))).order_by('subject_order')
        
        for cst_data in st_data:
            writer.writerow([student.name, student.surname, cst_data['subject__code'], cst_data['subject__fname'], cst_data['ractivity__name'], duration(cst_data['reqtime']), duration(cst_data['totaltime']), diffduration(cst_data['diff']), cst_data['last_time'], cst_data['alert']])

    return response

@login_required
def csv_export_pt(request, courseid):
    # Create the HttpResponse object with the appropriate CSV header.
    course = get_object_or_404(CourseType, id=courseid)
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="ProgressTests_{0}_{1}.csv"'.format(course.name, date.today())},
    )

    writer = csv.writer(response)
    writer.writerow(['Name', 'Surname', 'Code', 'Subject', 'Test', 'Status', 'Timestamp', 'Score', 'Attempts'])
    
    students = get_list_or_404(Student, course=courseid)
    data = dict()
    maxatt_q = ACELearnerJourney.objects.values('student', 'activity').annotate(Max('attempt')).filter(student_id=OuterRef('student_id'), activity_id=OuterRef('activity_id'))
    for student in students:
        data = ACEContentStatus.objects.filter(activity__subject__course__type=courseid, student_id=student.id).values('activity__subject__course__subject_order', 'activity__subject__code', 'activity__subject__fname', 'student__id', 'activity__name', 'status__name', 'timestamp', 'score').annotate(max_attempt=Subquery(maxatt_q.values('attempt__max'))).order_by('student_id', 'activity__subject__course__subject_order', 'activity__ord')
        for row in data:
            writer.writerow([student.name, student.surname, row['activity__subject__code'], row['activity__subject__fname'], row['activity__name'], row['status__name'].upper(), row['timestamp'], row['score'], row['max_attempt']])

    return response
