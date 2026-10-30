import base64
import io
import threading

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from fasthtml.common import (  # noqa: E402
    Div, Img, Input, Label, Option, Select, Table, Tbody, Td, Th, Thead, Tr,
)

# pyplot is global state, so draw one chart at a time
_plot_lock = threading.Lock()


class BaseComponent:
    def build_component(self, entity_id, model):
        return Div()

    def __call__(self, entity_id, model):
        return self.build_component(entity_id, model)


class Dropdown(BaseComponent):
    id = "selector"
    name = "user_selection"
    label = ""

    def component_data(self, entity_id, model):
        return model.names()

    def build_options(self, entity_id, model):
        return [
            Option(text, value=str(value), selected=(value == entity_id))
            for text, value in self.component_data(entity_id, model)
        ]

    def build_component(self, entity_id, model):
        return Div(
            Label(self.label, _for=f"{self.id}-select"),
            Select(*self.build_options(entity_id, model),
                   id=f"{self.id}-select", name=self.name),
            id=self.id,
        )


class Radio(BaseComponent):
    def __init__(self, values, name, hx_get="", hx_target="", hx_swap="outerHTML"):
        self.values = values
        self.name = name
        self.hx_get = hx_get
        self.hx_target = hx_target
        self.hx_swap = hx_swap

    def build_component(self, entity_id, model):
        current = model.name.capitalize() if model is not None else None
        buttons = [
            Label(
                Input(type="radio", name=self.name, value=value,
                      checked=(value == current), hx_get=self.hx_get,
                      hx_target=self.hx_target, hx_swap=self.hx_swap),
                value,
            )
            for value in self.values
        ]
        return Div(*buttons, cls="radio-group")


class MatplotlibViz(BaseComponent):
    def visualization(self, asset_id, model):
        raise NotImplementedError

    def describe(self, asset_id, model):
        return "Chart"

    def set_axis_styling(self, ax, border_color="#c9c8c3", font_color="#52514e"):
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(border_color)
            ax.spines[side].set_linewidth(1)
        ax.tick_params(colors=font_color, labelsize=9, length=0, pad=6)
        ax.xaxis.label.set_color(font_color)
        ax.yaxis.label.set_color(font_color)

    def build_component(self, asset_id, model):
        with _plot_lock:
            plt.close("all")
            self.visualization(asset_id, model)
            fig = plt.gcf()
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=150,
                        facecolor=fig.get_facecolor())
            plt.close(fig)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return Div(
            Img(src=f"data:image/png;base64,{encoded}",
                alt=self.describe(asset_id, model)),
            cls="chart-card",
        )


class DataTable(BaseComponent):
    def component_data(self, entity_id, model):
        raise NotImplementedError

    def build_component(self, entity_id, model):
        df = self.component_data(entity_id, model)
        head = Thead(Tr(*[Th(col.replace("_", " ").title(), scope="col")
                          for col in df.columns]))
        body = Tbody(*[
            Tr(*[Td(str(value)) for value in row])
            for row in df.itertuples(index=False, name=None)
        ])
        return Div(Table(head, body), cls="table-wrap")
