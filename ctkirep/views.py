from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.shortcuts import render, get_list_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Sum, F,  OuterRef, Subquery, Max

from ctkirep.forms import UploadFileForm, PTFileForm
from ctkirep.utils import bulk_reading_time, ace_contentstatus, ace_journeyreport
from ctkirep.models import ReadingTime, CourseType, Student, Course, ACEContentStatus,ACELearnerJourney

    #path("accounts/login/", auth_views.LoginView.as_view(template_name='ctkirep/login.html'), name='login'),
    #path("accounts/logout/", auth_views.LogoutView.as_view(), name='logout'),
    #path("accounts/password_change/", auth_views.PasswordChangeView.as_view(template_name='ctkirep/change_password.html', success_url='home'), name='password_change'),
#========================================================================
class CTKIRepLoginView(LoginView):
    template = 'ctkirep/login.html'

class CTKIRepPassChangeView(PasswordChangeView):
    template_name='ctkirep/change_password.html'
    success_url = reverse_lazy('home')
#========================================================================
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
        students = get_list_or_404(Student, course=self.kwargs['course'])
        context['students'] = students
        data = dict()
        for student in students:
            rt = ReadingTime.objects.values('student_id', 'activity_id').annotate(totaltime=Sum('duration')).filter(student_id=student.id, activity_id=OuterRef('ractivity_id'))
            st_data = Course.objects.filter(type=self.kwargs['course']).values('subject_order', 'subject__id', 'subject__code', 'subject__fname', 'ractivity__name', 'reqtime', 'ractivity_id').annotate(totaltime=Subquery(rt.values('totaltime'))).annotate(diff=F('totaltime')-F('reqtime')).order_by('subject_order')
            data[student.id] = st_data
        context['data'] = data
        context['coursetypes'] = CourseType.objects.order_by('sorder')
        context['subject_name'] = CourseType.objects.get(pk=self.kwargs['course']).name
        return context

@login_required
def reading_time_upload(request):
    res = ''
    course_types = CourseType.objects.order_by('sorder')
    context = {'coursetypes': course_types,}
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upl_file = form.save(commit=False)
            upl_file.save()
            res = bulk_reading_time(upl_file.file.path)
    
    form = UploadFileForm(initial={'upload_status': res, 'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")})
    context['form'] = form
    return render(request, 'ctkirep/reading_time_upload.html', context)
#========================================================================
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
        students = get_list_or_404(Student, course=self.kwargs['course'])
        data = dict()
        maxatt_q = ACELearnerJourney.objects.values('student', 'activity').annotate(Max('attempt')).filter(student_id=OuterRef('student_id'),activity_id=OuterRef('activity_id'))
        for student in students:
            data[student.id] = ACEContentStatus.objects.filter(activity__subject__course__type=self.kwargs['course'], student_id=student.id).values('activity__subject__course__subject_order', 'activity__subject__code', 'activity__subject__fname', 'student__id', 'activity__name','status__name', 'timestamp', 'score').annotate(max_attempt=Subquery(maxatt_q.values('attempt__max'))).order_by('student_id', 'activity__subject__course__subject_order', 'activity__ord')
        context['data'] = data
        context['students'] = students
        context['coursetypes'] = CourseType.objects.order_by('sorder')
        context['subject_name'] = CourseType.objects.get(pk=self.kwargs['course']).name
        return context

@login_required
def content_status_upload(request, rtype):
    res = ''
    course_types = CourseType.objects.order_by('sorder')
    context = {'coursetypes': course_types,}
    if request.method == 'POST':
        form = PTFileForm(request.POST, request.FILES)
        if form.is_valid():
            upl_file = form.save(commit=False)
            upl_file.save()
            if rtype == 1:
                res = ace_contentstatus(upl_file.file.path)
            else:
                res = ace_journeyreport(upl_file.file.path)
    
    form = PTFileForm(initial={'upload_status': res, 'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")})
    context['form'] = form
    if rtype == 1:
        context['label'] = 'Content status upload'
    else:
        context['label'] = 'Student journey upload'

    return render(request, 'ctkirep/progress_tests_upload.html', context)
#========================================================================
class StudentsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'ctkirep/students_home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_types = CourseType.objects.order_by('sorder')
        context['coursetypes'] = course_types
        return context

class StudentsTableView(LoginRequiredMixin, TemplateView):
    template_name = "ctkirep/reading_time_report.html"
    students = Student.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = get_list_or_404(Student, course=self.kwargs['course'])
        context['students'] = students
        return context