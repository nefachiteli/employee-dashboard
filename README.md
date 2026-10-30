# Employee Performance Dashboard

A FastHTML dashboard for tracking employee and team performance and the
predicted risk of an employee being recruited by a competitor.

## Features

* Switch between an employee view and a team view.
* Cumulative positive and negative events over time.
* Predicted recruitment risk (team view shows the average across members).
* Manager notes for the selected employee or team.

## Project layout

```
.
├── python-package/
│   ├── setup.py
│   └── employee_events/
│       ├── sql_execution.py
│       ├── query_base.py
│       ├── employee.py
│       ├── team.py
│       └── employee_events.db
├── report/
│   ├── dashboard.py
│   ├── utils.py
│   └── src/
│       ├── base_components.py
│       └── combined_components.py
├── assets/model.pkl
├── tests/
├── tools/make_placeholder_model.py
├── requirements.txt
└── .github/workflows/tests.yml
```

## Database

| Table | Columns |
|---|---|
| `team` | team_id, team_name, shift, manager_name |
| `employee` | employee_id, first_name, last_name, team_id |
| `employee_events` | event_date, employee_id, team_id, positive_events, negative_events |
| `notes` | employee_id, team_id, note, note_date |

## Setup

Python 3.9+.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ./python-package
```

## Usage

```bash
python report/dashboard.py
```

The dashboard runs at <http://localhost:5001>. Pages are also available at
`/employee/<id>` and `/team/<id>`.

Run the tests with:

```bash
pytest
```

## Model

`assets/model.pkl` is a logistic regression trained on simulated data by
`tools/make_placeholder_model.py`. It takes `positive_events` and
`negative_events` as features, so any model with the same inputs can be
dropped in its place.
