import json
from typing import Optional

from django.forms import Widget


class SumWidget(Widget):
    class Media:
        js = ["assets/js/cw_sum_widget.js"]

    template_name = "cw_sum_widget.html"

    def __init__(self, target_inputs: Optional[list] = None, *args, **kwargs):
        self.target_inputs = [] if target_inputs is None else target_inputs
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["target_inputs"] = json.dumps(self.target_inputs)
        return context


class RequestWidget(Widget):
    class Media:
        js = ["assets/js/cw_request_widget.js"]

    template_name = "cw_request_widget.html"

    def __init__(self, target_input: str, endpoint: str, *args, **kwargs):
        self.target_input = target_input
        self.endpoint = endpoint
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["target_input"] = self.target_input
        context["widget"]["endpoint"] = self.endpoint
        return context
