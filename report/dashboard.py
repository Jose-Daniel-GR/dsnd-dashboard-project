from fasthtml.common import *
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Import QueryBase, Employee, Team from employee_events
from employee_events.employee import Employee
from employee_events.team import Team
from employee_events.query_base import QueryBase

# Import the load_model function from utils.py
from utils import load_model

from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Subclass of Dropdown for report selection
class ReportDropdown(Dropdown):

    def build_component(self, entity_id, model):
        # Set label to the model's name attribute
        self.label = model.name
        # Return parent class build_component output
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        # Return names and ids for the given user type
        return model.names()


# Subclass of BaseComponent for page header
class Header(BaseComponent):

    def build_component(self, entity_id, model):
        # Return H1 with dynamic title based on model name
        if model.name == "employee":
            title = "Employee Performance"
        else:
            title = "Team Performance"
        return H1(title)


# Subclass of MatplotlibViz for cumulative event line chart
class LineChart(MatplotlibViz):

    def visualization(self, asset_id, model):
        # Set dark background style
        plt.style.use('dark_background')

        # Get event counts data for the given entity id
        df = model.event_counts(asset_id)

        # Fill null values with 0
        df = df.fillna(0)

        # Set event_date as index
        df = df.set_index('event_date')

        # Sort the index
        df = df.sort_index()

        # Convert to cumulative counts
        df = df.cumsum()

        # Rename columns
        df.columns = ['Positive', 'Negative']

        # Initialize matplotlib subplot with dark background
        fig, ax = plt.subplots(facecolor='#1a1d2e')
        ax.set_facecolor('#1a1d2e')

        # Plot cumulative counts
        df.plot(ax=ax)

        # Set white axis elements
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')

        # Apply axis styling
        self.set_axis_styling(ax, bordercolor='white', fontcolor='white')

        # Set title and axis labels
        ax.set_title('Cumulative Event Counts')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Count')


# Subclass of MatplotlibViz for ML recruitment risk bar chart
class BarChart(MatplotlibViz):

    # Load trained ML model as class attribute
    predictor = load_model()

    def visualization(self, asset_id, model):
        # Set dark background style
        plt.style.use('dark_background')

        # Get data for ML model prediction
        data = model.model_data(asset_id)

        # Generate prediction probabilities
        predictions = self.predictor.predict_proba(data)

        # Get second column - recruitment probability
        probs = predictions[:, 1]

        # For teams show mean, for employees show first value
        if model.name == 'team':
            pred = float(probs.mean())
        else:
            pred = float(probs[0])

        # Apply color scale based on risk level
        if pred < 0.33:
            color = 'green'
        elif pred < 0.66:
            color = 'orange'
        else:
            color = 'red'

        # Initialize matplotlib subplot with dark background
        fig, ax = plt.subplots(facecolor='#1a1d2e')
        ax.set_facecolor('#1a1d2e')

        # Draw slim horizontal bar
        ax.barh([''], [pred], color=color, height=0.3)
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20, color='white')

        # Set white axis elements
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        ax.tick_params(colors='white')

        # Apply axis styling
        self.set_axis_styling(ax, bordercolor='white', fontcolor='white')


# Subclass of CombinedComponent combining both charts
class Visualizations(CombinedComponent):

    # List of initialized visualization components
    children = [LineChart(), BarChart()]

    # Keep unchanged
    outer_div_type = Div(cls='grid')


# Subclass of DataTable for employee/team notes
class NotesTable(DataTable):

    def component_data(self, entity_id, model):
        # Return notes for the given entity id
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]


# Subclass of CombinedComponent for full dashboard report
class Report(CombinedComponent):

    # List of all dashboard components in display order
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable(),
        Footer(P("by José Daniel Gutiérrez R."))
    ]


# Initialize FastHTML app
app, rt = FastHTML(hdrs=[Link(rel='stylesheet', href='/assets/report.css')]), None
css_path = Path(__file__).parent.parent / 'assets' / 'report.css'
css_content = css_path.read_text()
app = FastHTML(hdrs=[Style(css_content)])

# Initialize Report instance
report = Report()


# Route for root path - defaults to employee id 1
@app.get('/')
def index():
    # Return report for employee with id 1
    return report(1, Employee())


# Route for individual employee pages
@app.get('/employee/{id}')
def employee(id: str):
    return report(int(id), Employee())


# Route for individual team pages
@app.get('/team/{id}')
def team(id: str):
    return report(int(id), Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()