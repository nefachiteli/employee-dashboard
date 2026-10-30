"""Employee performance and recruitment-risk dashboard.

Start with `python report/dashboard.py` and open http://localhost:5001.
"""
from functools import partial

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, PercentFormatter
import pandas as pd
from fasthtml.common import (
    FastHTML, H1, H2, HTMLResponse, Link, Main, Meta, P, RedirectResponse,
    Style, serve, to_xml,
)

from employee_events import Employee, QueryBase, Team
from utils import load_model
from src.base_components import (
    BaseComponent, DataTable, Dropdown, MatplotlibViz, Radio,
)
from src.combined_components import CombinedComponent, FormGroup

# chart colours
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_MUTED = "#52514e"
GRID = "#e4e3df"
POSITIVE = "#2a78d6"
NEGATIVE = "#eb6834"
TRACK = "#e4e3df"
RISK_LOW = "#2a78d6"
RISK_MODERATE = "#fab219"
RISK_HIGH = "#d03b3b"


def _compact(value, _pos=None):
    """Axis tick formatter: 1500 -> 1.5K."""
    if abs(value) >= 1000:
        return f"{value / 1000:g}K"
    return f"{value:g}"


class ReportDropdown(Dropdown):
    """Dropdown listing either employees or teams."""

    def build_component(self, entity_id, model):
        self.label = model.name.capitalize()
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()


class Header(BaseComponent):
    """Page title with the selected employee or team name."""

    def build_component(self, entity_id, model):
        name = model.username(entity_id)[0][0]
        return Main(
            H1(name),
            P(f"{model.name.capitalize()} performance and recruitment risk",
              cls="subtitle"),
        )


class LineChart(MatplotlibViz):
    """Cumulative positive and negative events over time."""

    def visualization(self, asset_id, model):
        df = model.event_counts(asset_id).fillna(0)
        df["event_date"] = pd.to_datetime(df["event_date"])
        df = df.set_index("event_date").sort_index().cumsum()
        df.columns = ["Positive", "Negative"]

        fig, ax = plt.subplots(figsize=(6, 3.4), facecolor=SURFACE)
        ax.set_facecolor(SURFACE)

        ax.plot(df.index, df["Positive"], color=POSITIVE, linewidth=1.8,
                solid_capstyle="round", label="Positive")
        ax.plot(df.index, df["Negative"], color=NEGATIVE, linewidth=1.8,
                solid_capstyle="round", label="Negative")

        for column, colour in (("Positive", POSITIVE), ("Negative", NEGATIVE)):
            ax.plot(df.index[-1], df[column].iloc[-1], "o", color=colour,
                    markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.5)

        # only label the line ends when they do not overlap
        top = max(df["Positive"].iloc[-1], df["Negative"].iloc[-1], 1)
        gap = abs(df["Positive"].iloc[-1] - df["Negative"].iloc[-1])
        if gap > 0.12 * top:
            for column in ("Positive", "Negative"):
                ax.annotate(f"{int(df[column].iloc[-1]):,}",
                            (df.index[-1], df[column].iloc[-1]),
                            xytext=(8, 0), textcoords="offset points",
                            va="center", fontsize=9, color=INK)

        self.set_axis_styling(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(FuncFormatter(_compact))
        locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        ax.margins(x=0.02)
        ax.set_xlim(right=df.index[-1] + (df.index[-1] - df.index[0]) * 0.10)

        ax.set_title("Cumulative events", loc="left", fontsize=12,
                     fontweight="bold", color=INK, pad=14)
        ax.set_ylabel("Events")
        ax.legend(loc="upper left", frameon=False, fontsize=9,
                  labelcolor=INK_MUTED, handlelength=1.6)
        fig.tight_layout()

    def describe(self, asset_id, model):
        df = model.event_counts(asset_id).fillna(0)
        return (f"Line chart of cumulative events. Total positive events: "
                f"{int(df['positive_events'].sum()):,}. Total negative "
                f"events: {int(df['negative_events'].sum()):,}.")


class BarChart(MatplotlibViz):
    """Predicted recruitment risk shown as a 0-100% bar."""

    predictor = load_model()

    def predict_risk(self, asset_id, model):
        """Return (mean risk, number of rows scored).

        A team has one row per employee, so its risk is the average.
        """
        data = model.model_data(asset_id).dropna()
        if data.empty:
            return None, 0
        probabilities = self.predictor.predict_proba(data)[:, 1]
        return float(probabilities.mean()), len(probabilities)

    @staticmethod
    def band(risk):
        """Map a risk value to a (label, colour) pair."""
        if risk < 1 / 3:
            return "Low", RISK_LOW
        if risk < 2 / 3:
            return "Moderate", RISK_MODERATE
        return "High", RISK_HIGH

    def visualization(self, asset_id, model):
        risk, people = self.predict_risk(asset_id, model)

        fig, ax = plt.subplots(figsize=(6, 3.4), facecolor=SURFACE)
        ax.set_facecolor(SURFACE)
        ax.set_title("Predicted recruitment risk", loc="left", fontsize=12,
                     fontweight="bold", color=INK, pad=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])

        if risk is None:
            ax.text(0.5, 0, "No event data", ha="center", va="center",
                    color=INK_MUTED, fontsize=11)
            ax.set_xticks([])
        else:
            label, colour = self.band(risk)
            ax.barh([0], [1], height=0.22, color=TRACK)
            ax.barh([0], [risk], height=0.22, color=colour)
            ha = "right" if risk > 0.8 else "left"
            ax.text(risk + (-0.01 if ha == "right" else 0.01), 0.17,
                    f"{risk:.0%}  {label} risk", ha=ha, va="bottom",
                    fontsize=11, fontweight="bold", color=INK)
            if model.name == "team":
                ax.text(0, -0.30, f"Average across {people} employees",
                        fontsize=9, color=INK_MUTED, va="top")
            ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
            ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))

        self.set_axis_styling(ax)
        ax.spines["left"].set_visible(False)
        fig.tight_layout()

    def describe(self, asset_id, model):
        risk, _ = self.predict_risk(asset_id, model)
        if risk is None:
            return "Predicted recruitment risk: no event data."
        label, _ = self.band(risk)
        return f"Predicted recruitment risk is {risk:.0%} ({label})."


class Visualizations(CombinedComponent):
    """Both charts side by side."""

    children = [LineChart(), BarChart()]
    outer_div_type = staticmethod(partial(Main, cls="grid-2"))


class NotesHeading(BaseComponent):
    def build_component(self, entity_id, model):
        return H2("Manager notes")


class NotesTable(DataTable):
    """Table of manager notes."""

    def component_data(self, entity_id, model):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):
    """Employee/Team toggle, name dropdown and Update button."""

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        # switching the radio reloads the dropdown via htmx
        Radio(values=["Employee", "Team"], name="profile_type",
              hx_get="/update_dropdown", hx_target="#selector",
              hx_swap="outerHTML"),
        ReportDropdown(),
    ]


class Report(CombinedComponent):
    """The full dashboard page."""

    children = [Header(), DashboardFilters(), Visualizations(),
                NotesHeading(), NotesTable()]
    outer_div_type = staticmethod(partial(Main, cls="container"))


CSS = f"""
:root {{ color-scheme: light; }}
body {{ background: #f4f3ef; }}
.subtitle {{ color: {INK_MUTED}; margin-top: -0.5rem; }}
#top-filters {{ display: flex; flex-wrap: wrap; gap: 1.5rem;
               align-items: end; margin-bottom: 1.5rem; }}
#top-filters button {{ width: auto; margin-bottom: var(--pico-spacing); }}
.radio-group {{ display: flex; gap: 1.5rem; }}
.grid-2 {{ display: grid; gap: 1rem; padding: 0;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }}
.chart-card {{ background: {SURFACE}; border: 1px solid {GRID};
              border-radius: 8px; padding: 0.5rem; }}
.chart-card img {{ display: block; width: 100%; height: auto; }}
.table-wrap {{ max-height: 380px; overflow: auto; }}
"""

PICO = Link(rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css")

app = FastHTML(
    title="Employee Performance Dashboard",
    hdrs=(PICO, Meta(name="color-scheme", content="light"), Style(CSS)),
    htmlkw={"data-theme": "light"},
)

report = Report()


def _lookup(model, raw_id):
    """Return the id as an int if it exists in the database, else None."""
    try:
        entity_id = int(raw_id)
    except (TypeError, ValueError):
        return None
    return entity_id if model.username(entity_id) else None


def _not_found(kind):
    """404 page for an unknown employee or team."""
    page = Main(H1(f"{kind} not found"),
                P("Pick someone from the dashboard home page."),
                cls="container")
    return HTMLResponse(to_xml(page), status_code=404)


@app.get("/")
def index():
    """Home page, showing the first employee."""
    return report(1, Employee())


@app.get("/employee/{id}")
def employee(id: str):
    """Dashboard for a single employee."""
    entity_id = _lookup(Employee(), id)
    if entity_id is None:
        return _not_found("Employee")
    return report(entity_id, Employee())


@app.get("/team/{id}")
def team(id: str):
    """Dashboard for a single team."""
    entity_id = _lookup(Team(), id)
    if entity_id is None:
        return _not_found("Team")
    return report(entity_id, Team())


@app.get("/update_dropdown")
def update_dropdown(profile_type: str = "Employee"):
    """Return a dropdown of employees or teams for the htmx swap."""
    dropdown = DashboardFilters.children[1]
    model = Team() if profile_type == "Team" else Employee()
    return dropdown(None, model)


@app.post("/update_data")
def update_data(profile_type: str = "Employee", user_selection: str = "1"):
    """Redirect to the page for the selected employee or team."""
    path = "team" if profile_type == "Team" else "employee"
    return RedirectResponse(f"/{path}/{user_selection}", status_code=303)


if __name__ == "__main__":
    serve()
