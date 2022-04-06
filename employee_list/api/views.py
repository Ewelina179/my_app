import csv

from rest_framework import viewsets
from django.db.models import Avg, ProtectedError, Subquery
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, Http404, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist, BadRequest

from .forms import EmployeeForm
from employees.models import Employee, Profession
from .serializers import EmployeeSerializer, ProfessionSerializer


def handler400(request, exception=None):
    context = {
       "message": exception
    }
    return render(request, "400.html", context)

def handler404(request, exception):
    context = {
       "message": exception
    }
    return render(request, "404.html", context)

def handler500(request):
    return render(request, "500.html")

class EmployeeView(View):

    def get(self, request, *args, **kwargs):
        get_object_or_404(self.model, id=kwargs['pk']) 
        return super().get(request, *args, **kwargs)


class EmployeeListView(ListView):

    model = Employee
    template_name = 'employee/list_of_employees.html'
    paginate_by = 10
    ordering = ['last_name']
    
    
class EmployeeView(EmployeeView, DetailView):

    model = Employee
    context_object_name = 'employee'
    template_name = "employee/employee_detail.html"


class CreateEmployeeView(CreateView):

    model = Employee
    form_class = EmployeeForm
    success_url = "/"
    template_name = "employee/employee_create_form.html"


class UpdateEmployeeView(EmployeeView, UpdateView):

    model = Employee
    fields = ['first_name', 'last_name', 'age', 'profession', 'avatar']
    success_url = "/"
    template_name = "employee/employee_update_form.html"


class DeleteEmployeeView(DeleteView):

    model = Employee
    success_url = "/"
    template_name = "employee/employee_delete.html"

    
class ReportView(View):

    def get(self, request):
        avg = Employee.objects.all().values('profession').annotate(Avg('age')).order_by('profession_id')
        a = Profession.objects.filter(id__in=Subquery(avg.values('profession'))).all().order_by('id')
        lst = [list(avg), list(a)]
        avg_and_profession_name = zip(*lst)
        context = {
            "avg_and_profession_name": avg_and_profession_name

        }
        return render(request, "employee/report.html", context)


class ReportFileView(View):

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="raport.csv"'
        avg = Employee.objects.values("profession__name").annotate(avg_age=Avg("age"))
        writer = csv.writer(response)
        for element in avg:
            writer.writerow((element["profession__name"], element["avg_age"]))
        return response


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class DeleteEmployeeAjaxView(View):
    
    def get(self, request, pk):
        try:
            employee_to_delete = Employee.objects.get(id = pk)
        except Employee.DoesNotExist:
            return JsonResponse({"message": "Employee not found."})
        if is_ajax(request=request):
            employee_to_delete.delete()
            response = {"message": "Employee deleted"}
        else:
            response = {"message": "Wroung route\Deleting available through ajax"}
        return JsonResponse(response)


class ProfessionListView(ListView):

    model = Profession
    template_name = 'profession/list_of_professions.html'
    paginate_by = 10
    ordering = ['name']


class CreateProfessionView(CreateView):

    model = Profession
    fields = ['name']
    success_url = "/"
    template_name = "profession/profession_create.html"


class UpdateProfessionView(UpdateView):

    model = Profession
    fields = ['name']
    success_url = "/"
    template_name = "profession/profession_update.html"


class DeleteProfessionView(DeleteView):

    model = Profession
    success_url = "/"
    template_name = "employee/employee_delete.html"

    def post(self, request, pk, *args, **kwargs):
        try:
            self.delete(request, *args, **kwargs)
        except ProtectedError:
            raise BadRequest("Nie można usunąć zawodu, bo ma przypisanego pracownika.")
        return HttpResponse("Usunięto zawód")


class EmployeeViewset(viewsets.ModelViewSet):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class ProfessionViewSet(viewsets.ModelViewSet):

    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

    def get_serializer_context(self):
        return {'request': self.request}