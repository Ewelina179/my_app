from django.forms import ModelForm
from django import forms
from .models import Employee

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'age', 'profession', 'avatar']

FILE_FORMAT = (
    ("pdf", "pdf"),
    ("csv", "csv")
)

class GetReportForm(ModelForm):
    file_format = forms.ChoiceField(choices = FILE_FORMAT)

    class Meta:
        model = Employee
        fields = ['profession']


