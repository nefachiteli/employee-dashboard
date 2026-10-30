from fasthtml.common import Button, Div, Form

from .base_components import BaseComponent


class CombinedComponent(BaseComponent):
    children = []
    outer_div_type = staticmethod(Div)

    def call_children(self, entity_id, model):
        return [child(entity_id, model) for child in self.children]

    def build_component(self, entity_id, model):
        return self.outer_div_type(*self.call_children(entity_id, model))


class FormGroup(CombinedComponent):
    id = ""
    action = ""
    method = "POST"

    def build_component(self, entity_id, model):
        return Form(
            *self.call_children(entity_id, model),
            Button("Update", type="submit"),
            id=self.id, action=self.action, method=self.method,
        )
