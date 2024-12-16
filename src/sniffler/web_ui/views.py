from django.contrib import messages
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = "web_ui/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.info(self.request, "hello http://example.com")
        return context
