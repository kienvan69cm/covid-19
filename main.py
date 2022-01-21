from turtle import width
import requests
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
import plotly.graph_objects as go
from streamlit_folium import folium_static
st.set_page_config(page_title="Covid-19",
                   layout="wide")


# SIDEBAR

st.title("Worldwide")
res = requests.get('https://disease.sh/v3/covid-19/all')
ww = res.json()
col1, col2, col3 = st.columns(3)
col1.metric("Total cases", ww["cases"], ww["todayCases"])
col2.metric("Deaths", ww["deaths"], ww["todayDeaths"])
col3.metric("Recoverd", ww["recovered"], ww["todayRecovered"])

# GET DATA
res = requests.get('https://disease.sh/v3/covid-19/countries')
covid_current = res.json()
features = ["country", "cases", "deaths", "recovered"]
covid_df = pd.DataFrame(covid_current)
minimal_covid_df = covid_df[features]
covid_df = covid_df.drop(columns=["updated", "countryInfo"])

# TABLE


st.title("Global Data")
st.dataframe(minimal_covid_df)
st.title("Country Data")
selected_country = st.selectbox(
    "Country", covid_df["country"])
df_selection = covid_df.query(
    "country==@selected_country"
)
if selected_country != "Global":
    st.dataframe(df_selection)

# CHART
st.title("Chart")
chart_type = st.selectbox(
    "Case Type", ("cases", "deaths"))
selected_time = st.selectbox(
    "Time", ["last 7 days", "last 30 days"])
res = requests.get(
    f'https://disease.sh/v3/covid-19/historical/{selected_country}?lastdays=all')
country_historical = res.json()
df = []
for day, type in country_historical["timeline"][chart_type].items():
    df.append([day, type])
country_df = pd.DataFrame(df, columns=["Day", chart_type])
if selected_time == "last 7 days":
    time = 7
else:
    time = 30
fig = px.line(
    country_df, country_df.Day[-time:], country_df[chart_type][-time:])
fig.update_layout(yaxis_title=None, xaxis_title=None)
col1, col2 = st.columns([3, 1])
col1.subheader(chart_type+" chart in " + selected_time)
col1.plotly_chart(fig, use_container_width=True)
col2.subheader(chart_type+" data")
col2.dataframe(country_df[::-1])


def set_color(type):
    if type == "cases" or type == "todayCases":
        return "YlOrBr"
    if type == "deaths" or type == "todayDeaths":
        return "Reds"
    return "Blues"


# MAP
st.title("Map")
map_type = st.selectbox(
    "Case Type", ("cases", "deaths", "recovered", "todayCases", "todayDeaths", "todayRecovered"))
st.subheader(map_type+" heat map")
m = folium.Map(location=[1.185474, 28.165547], zoom_start=2)
folium.Choropleth(
    geo_data="world-countries.json",
    name='choropleth COVID-19',
    data=covid_df,
    columns=['country', map_type],
    key_on='feature.properties.name',
    fill_color=set_color(map_type),
    nan_fill_color='white'
).add_to(m)
folium.features.GeoJson(
    data=open('world-countries.json', 'r', encoding='utf-8-sig').read(),
    name='Covid',
    smooth_factor=2,
    style_function=lambda x: {'color': 'black',
                              'fillColor': 'transparent', 'weight': 0.5},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name'
                ],
        aliases=["Country: "
                 ],
        localize=True,
        sticky=False,
        labels=True,
        style="""
                            background-color: #F0EFEF;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """,
        max_width=1000,),
    highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
).add_to(m)
folium.TileLayer('cartodbpositron').add_to(m)
folium_static(m, width=1200, height=700)
