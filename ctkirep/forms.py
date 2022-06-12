from datetime import date
from django import forms

from ctkirep.models import ReadingTimeUpload, PTUpload, Student

class UploadFileForm(forms.ModelForm):
    upload_status = forms.CharField(label="Upload status:", disabled=True, required=False, widget=forms.TextInput(attrs={'style': 'border-style:none; width: 100%'}))
    class Meta:
        model = ReadingTimeUpload
        fields = ['timestamp', 'file']
        widgets = {
            'timestamp': forms.TextInput(attrs={'readonly': True}),
            'file' : forms.FileInput(attrs={'accept': '.xml'})
        }

class RTExportForm(forms.Form):
    def __init__(self, course_types, *args, **kwargs):
        super(RTExportForm, self).__init__(*args, **kwargs)
        self.fields['course'].choices = course_types

    course = forms.ChoiceField(label="Course type", choices=())
    start_date = forms.DateField(label='Start date', input_formats=['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d'], initial=date(2022, 3, 22), widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End date', input_formats=['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d'], initial=date.today(), widget=forms.DateInput(attrs={'type': 'date'}))

class PTFileForm(forms.ModelForm):
    upload_status = forms.CharField(label="Upload status:", disabled=True, required=False, widget=forms.TextInput(attrs={'style': 'border-style:none; width: 100%'}))
    class Meta:
        model = PTUpload
        fields = ['timestamp', 'file']
        widgets = {
            'timestamp': forms.TextInput(attrs={'readonly': True}),
            'file' : forms.FileInput(attrs={'accept': '.csv'})
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'surname', 'email_addr', 'reading_username', 'pt_username', 'course', 'start_date']
