import json

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from sniffler.core.stats import StatCalculator
from sniffler.core.utils import convert_size

from .forms import ScanForm
from .models import ScanResult
from .tasks import run_scan
from .utils import CollectionJSONEncoder


class HomePageView(TemplateView):
    template_name = "web_ui/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ScanView(FormMixin, ListView):  # Change inheritance to FormMixin and ListView
    template_name = "web_ui/scan.html"
    form_class = ScanForm
    success_url = reverse_lazy("scan")
    model = ScanResult
    context_object_name = "scans"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if "scan_id" in request.POST:
            scan_id = request.POST.get("scan_id")
            try:
                ScanResult.objects.get(id=scan_id)  # Validate scan_id exists
                request.session["active_scan_id"] = scan_id
                messages.success(request, "Active scan set successfully.")
            except ScanResult.DoesNotExist:
                messages.error(request, "Selected scan does not exist.")
            return redirect("scan")
        elif "remove_scan_id" in request.POST:
            remove_scan_id = request.POST.get("remove_scan_id")
            if remove_scan_id:
                ScanResult.objects.filter(id=remove_scan_id).delete()
                messages.success(request, "Scan removed successfully.")
            return redirect("scan")
        else:
            self.object_list = self.get_queryset()
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        path = form.cleaned_data["path"]
        try:
            scan_result = run_scan(path)
        except FileNotFoundError:
            messages.error(self.request, "Path not found.")
            return self.form_invalid(form)
        except Exception:  # Handle all other exceptions
            messages.error(self.request, "An error occurred during scanning.")
            return self.form_invalid(form)

        scan_instance = ScanResult.objects.create(path=path, result=json.dumps(scan_result, cls=CollectionJSONEncoder))
        self.request.session["active_scan_id"] = scan_instance.id
        messages.success(self.request, "Scan completed successfully and set as active.")
        return HttpResponseRedirect(self.get_success_url())


class StatsView(TemplateView):
    template_name = "web_ui/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_scan_id = self.request.session.get("active_scan_id")
        if active_scan_id:
            try:
                scan = ScanResult.objects.get(id=active_scan_id)
                collection = json.loads(scan.result)
                stats_calculator = StatCalculator(collection)

                context["total_size"] = convert_size(stats_calculator.total_size())
                context["count_by_extension"] = stats_calculator.count_by_extension().most_common()
                context["top_largest_files"] = stats_calculator.top_n_largest_files(10)
                context["top_largest_images"] = stats_calculator.top_n_largest_images(10)
                context["top_documents_by_pages"] = stats_calculator.top_n_documents_by_pages(10)
            except ScanResult.DoesNotExist:
                context["error"] = "Active scan not found. Please run a new scan, or select one from Scans."
            except json.JSONDecodeError:  # Catch JSON decoding errors
                context["error"] = "Invalid scan data encountered."
        else:
            context["error"] = "No active scan. Please run a new scan, or select one from Scans."
        return context
