import json

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
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


class ScanView(FormView, ListView):
    template_name = "web_ui/scan.html"
    form_class = ScanForm
    success_url = reverse_lazy("scan")
    model = ScanResult
    context_object_name = "scans"

    def form_valid(self, form):
        self.object_list = self.get_queryset()
        path = form.cleaned_data["path"]
        try:
            scan_result = run_scan(path)
        except FileNotFoundError:
            messages.error(self.request, "Path not found.")
            return super().form_invalid(form)

        scan_instance = ScanResult.objects.create(path=path, result=json.dumps(scan_result, cls=CollectionJSONEncoder))
        self.request.session["active_scan_id"] = scan_instance.id
        messages.success(self.request, "Scan completed successfully and set as active.")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if "scan_id" in request.POST:
            scan_id = request.POST.get("scan_id")
            if scan_id:
                request.session["active_scan_id"] = scan_id
                messages.success(request, "Active scan set successfully.")
        else:
            return super().post(request, *args, **kwargs)
        return redirect("scan")


class StatsView(TemplateView):
    template_name = "web_ui/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_scan_id = self.request.session.get("active_scan_id")
        if active_scan_id:
            scan = ScanResult.objects.get(id=active_scan_id)
            collection = json.loads(scan.result)
            stats_calculator = StatCalculator(collection)

            context["total_size"] = convert_size(stats_calculator.total_size())
            context["count_by_extension"] = stats_calculator.count_by_extension().most_common()
            context["top_largest_files"] = stats_calculator.top_n_largest_files(10)
            context["top_largest_images"] = stats_calculator.top_n_largest_images(10)
            context["top_documents_by_pages"] = stats_calculator.top_n_documents_by_pages(10)
        return context
