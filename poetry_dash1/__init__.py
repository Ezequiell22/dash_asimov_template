import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import pathlib
from datetime import datetime as dt
import datetime
import numpy as np

app = dash.Dash(__name__)

#pre processamento
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

df = pd.read_csv(DATA_PATH.joinpath('clinical_analytics.csv'))
clinic_list = df["Clinic Name"].unique()
df["Admit Source"] = df["Admit Source"].fillna("Not identified")
admit_list = df["Admit Source"].unique()


df["Check-In Time"] = df["Check-In Time"].apply(
  lambda x: dt.strptime(x, "%Y-%m-%d %I:%M:%S %p")
)

df["Days of Wk"] = df["Check-In Time"]
df["Check-In Hour"] = df["Check-In Time"]

df["Days of Wk"] = df["Days of Wk"].apply(
  lambda x : dt.strftime(x, "%A")
)
df["Check-In Hour"] = df["Check-In Hour"].apply(
  lambda x : dt.strftime(x, "%I %p")
)

day_list = ["Monday", "Tuesday","Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]

check_in_duration = df["Check-In Time"].describe()
all_departaments = df["Department"].unique().tolist()

#layout
def description_card():
  return html.Div(id="description-cad", children=[
    html.H5("Clinical"),
    html.H3("Welcome"),
    html.Div(id='intro', children="Explore")
  ])

def generate_control_card():
  return html.Div(id='control-cad', children=[
    html.P("Select the clinic"),
    dcc.Dropdown(
      id='clinic-select',
      options=[{"label": i, "value": i} for i in clinic_list],
      value=clinic_list[0]
    ),
    html.P("Select the Check-In Time"),
    dcc.DatePickerRange(
      id='date-picker-select',
      start_date=df["Check-In Time"].min().date(),
      end_date=df["Check-In Time"].max().date(),
      min_date_allowed=df["Check-In Time"].min().date(),
      max_date_allowed=df["Check-In Time"].max().date(),
    ),
    html.P("Select Admit Source"),
    dcc.Dropdown(
      id='admit-select',
      options=[{"label": i, "value": i} for i in admit_list],
      value=admit_list[:],
      multi=True
    ),
  ])

#
def get_patient_volumn_headmap(start, end, clinic, admit_type_list):
  filter_df = df[(df["Clinic Name"] ==clinic) & (df["Admit Source"].isin(admit_type_list))]
  filter_df = filter_df.sort_values("Check-In Time").set_index("Check-In Time")[start:end]

  x_axis = [datetime.time(i).strftime("%I %p") for i in range(24)]
  y_axis = day_list

  #cria matriz 7 linhas X 24 colunas
  z = np.zeros((7,24)) 
  annotations = []

  for index_y, value_y in enumerate(y_axis):
    filter_day = filter_df[filter_df["Days of Wk"] == value_y]
    for index_x, value_x in enumerate(x_axis):
      sum_of_records = filter_day[filter_day["Check-In Hour"] == value_x]["Number of Records"].sum()
      z[index_y, index_x] = sum_of_records

      ann_dict = dict(
        showarrow=False,
        text="<b>" + str(sum_of_records) +"</b>",
        x=value_x,
        y=value_y
      )

      annotations.append(ann_dict)

  hovertemplate = "<b> %{y} %{x} <br><br> %{z} Patient"  
  data = [
    dict(
      x=x_axis,
      y=y_axis,
      z=z,
      type="headmap",
      hovertemplate=hovertemplate,
      showscale=False,
      colorscale=[[0, '#caf3ff'], [1, '#2c82ff']]
    )
  ]
  layout = dict(
    margin=dict(l=70, b=50, t=50, r=50),
    modebar={"orientation" : "v"},
    font=dict(family = "Open Sans"),
    annotations=annotations,
    xaxis=dict(
      side="Top",
      ticks="",
      ticklen=2,
      tickfont=dict(family="sans-serif"),
      tickcolor="#ffffff"
    ),
    yaxis=dict(
      side="left",
      ticks="",
      tickfont=dict(family="sans-serif"),
      ticksuffix=" "
    ),
    hovermode="closest",
    showlegend=False
  )

  return {"data" : data, "layout" : layout}



app.layout = html.Div(
  id='app-container',
  children=[
    html.Div(
      id='left-column',
      className='four columns',
      children=[description_card(), generate_control_card()]
    )
  ]
)

if __name__ == '__main__':
  app.run_server(debug=True)