from dataclasses import fields
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
