import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.colors
from collections import OrderedDict
import requests


# default list of all countries of interest
country_default = OrderedDict([('Canada', 'CAN'), ('United States', 'USA'), 
  ('Brazil', 'BRA'), ('France', 'FRA'), ('India', 'IND'), ('Italy', 'ITA'), 
  ('Germany', 'DEU'), ('United Kingdom', 'GBR'), ('China', 'CHN'), ('Japan', 'JPN')])


def return_figures(countries=country_default):
  """Creates four plotly visualizations using the World Bank API

  # Example of the World Bank API endpoint:
  # arable land for the United States and Brazil from 1990 to 2015
  # http://api.worldbank.org/v2/countries/usa;bra/indicators/AG.LND.ARBL.HA?date=1990:2015&per_page=1000&format=json

    Args:
        country_default (dict): list of countries for filtering the data

    Returns:
        list (dict): list containing the four plotly visualizations

  """

  # when the countries variable is empty, use the country_default dictionary
  if not bool(countries):
    countries = country_default

  # prepare filter data for World Bank API
  # the API uses ISO-3 country codes separated by ;
  country_filter = list(countries.values())
  country_filter = [x.lower() for x in country_filter]
  country_filter = ';'.join(country_filter)

  # World Bank indicators of interest for pulling data
  indicators = ['NY.GDP.MKTP.CD', 'SP.RUR.TOTL.ZS', 'SP.RUR.TOTL.ZS', 'AG.LND.FRST.ZS']

  data_frames = [] # stores the data frames with the indicator data of interest
  urls = [] # url endpoints for the World Bank API

  # pull data from World Bank API and clean the resulting json
  # results stored in data_frames variable
  for indicator in indicators:
    url = 'http://api.worldbank.org/v2/countries/' + country_filter +\
    '/indicators/' + indicator + '?date=1991:2016&per_page=1000&format=json'
    urls.append(url)

    try:
      r = requests.get(url)
      data = r.json()[1]
    except:
      print('could not load data ', indicator)

    for i, value in enumerate(data):
      value['indicator'] = value['indicator']['value']
      value['country'] = value['country']['value']

    data_frames.append(data)
  
  #########################################################
  # first chart plots arable land from 1990 to 2015 in top 10 economies 
  # as a line chart
  #########################################################
  graph_one = []
  df_one = pd.DataFrame(data_frames[0])

  # filter and sort values for the visualization
  # filtering plots the countries in decreasing order by their values
  # df_one = df_one[(df_one['date'] == '2015') | (df_one['date'] == '1990')]
  df_one.sort_values('value', ascending=False, inplace=True)

  # this  country list is re-used by all the charts to ensure legends have the same
  # order and color
  countrylist = df_one.country.unique().tolist()
  
  for country in countrylist:
      x_val = df_one[df_one['country'] == country].date.tolist()
      y_val =  df_one[df_one['country'] == country].value.tolist()
      graph_one.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines+markers',
          type = 'scatter',
          name = country
          )
      )

  layout_one = dict(title = 'Change in GDP in Various Countries from 1990 to 2015',
                xaxis = dict(title = 'Year',
                  autotick=False, tick0=1991, dtick=25),
                yaxis = dict(title = 'GDP'),
                )
  #########################################################
  # second chart plots ararble land for 2015 as a bar chart
  #########################################################
  graph_two = []
  df_one.sort_values('value', ascending=False, inplace=True)
  df_one = df_one[df_one['date'] == '2015'] 

  graph_two.append(
      go.Bar(
      x = df_one.country.tolist(),
      y = df_one.value.tolist(),
      marker =  {
      'color': '#1f77b4b',
      'line': {
          'width': 2
        }
      }
      )
  )

  layout_two = dict(title = 'Hectares Arable Land per Person in 2015',
                xaxis = dict(title = 'Country',),
                yaxis = dict(title = 'Hectares per person'),
                )
  #########################################################
  # third chart plots percent of population that is rural from 1990 to 2015
  #########################################################

  df_three = pd.DataFrame(data_frames[1])
  df_three = df_three[(df_three['date'] == '2015')]

  locations = []
  y_val = []
  for country in countrylist:
    locations.append(country_default[country])
    y_val.append(df_three[df_three['country'] == country].value.tolist()[0])

  graph_three = []
  graph_three.append(
      go.Scattergeo(
        locations = locations,
        marker = {
          'size': y_val,
          'color': [i*10 for i in y_val],
          'cmin': 0,
          'cmax': 100,
          'colorscale': 'Blue',
          'colorbar': {
            'title': 'Some rate',
            'ticksuffix': '%',
            'showticksuffix': 'last'
          },
          'line': {  
            'color': 'black'
          }
        },
        mode = 'markers',
        name = 'earth data'
      )
        )
  layout_three = {
    'geo': {
        'scope': 'earth',
        'resolution': 100
    }, 
    'title': 'Rural Population versus <br> Forested Area (Square Km) 1990-2015'
  }


  #########################################################
  # fourth chart shows rural population vs arable land as percents
  #########################################################
  graph_four = []
  df_four_a = pd.DataFrame(data_frames[2])
  df_four_a = df_four_a[['country', 'date', 'value']]
  
  df_four_b = pd.DataFrame(data_frames[3])
  df_four_b = df_four_b[['country', 'date', 'value']]

  df_four = df_four_a.merge(df_four_b, on=['country', 'date'])
  df_four.sort_values('date', ascending=True, inplace=True)

  plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS

  for i, country in enumerate(countrylist):

      current_color = []

      x_val = df_four[df_four['country'] == country].value_x.tolist()
      y_val = df_four[df_four['country'] == country].value_y.tolist()
      years = df_four[df_four['country'] == country].date.tolist()
      country_label = df_four[df_four['country'] == country].country.tolist()

      text = []
      for country, year in zip(country_label, years):
          text.append(str(country) + ' ' + str(year))

      graph_four.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines+markers',
          text = text,
          name = country,
          textposition = 'top'
          )
      )

  layout_four = dict(title = '% of Population that is Rural versus <br> % of Land that is Forested <br> 1990-2015',
                xaxis = dict(title = '% Population that is Rural', range=[0,100], dtick=10),
                yaxis = dict(title = '% of Area that is Forested', range=[0,100], dtick=10),
                )



  #########################################################
  # fourth chart shows rural population vs arable land as percents
  #########################################################
  locations = []
  for country in countrylist:
    locations.append(country_default[country])

  graph_five= []
  graph_five.append(
      go.Scattergeo(
        # locations = ['FRA', 'DEU', 'RUS', 'JPN', 'GBR', 'CHN', 'CAN', 'USA', 'BRA', 'IND'],
        locations = locations,
        marker = {
          'size': [20, 30, 15, 100, 80, 20, 30, 15, 100, 80],
          'color': [10, 20, 40, 50, 60, 20, 30, 15, 100, 80],
          'cmin': 0,
          'cmax': 100,
          'colorscale': 'Greens',
          'colorbar': {
            'title': 'Some rate',
            'ticksuffix': '%',
            'showticksuffix': 'last'
          },
          'line': {
            'color': 'black'
          }
        },
        mode = 'markers',
        name = 'earth data'
      )
        )
  layout_five = {
    'geo': {
        'scope': 'earth',
        'resolution': 100
    }, 
    'title': 'Rural Population versus <br> Forested Area (Square Km) 1990-2015'
  }

  #########################################################
  # append all charts
  #########################################################
  figures = []
  figures.append(dict(data=graph_one, layout=layout_one))
  figures.append(dict(data=graph_two, layout=layout_two))
  figures.append(dict(data=graph_three, layout=layout_three))
  figures.append(dict(data=graph_four, layout=layout_four))
  figures.append(dict(data=graph_five, layout=layout_five))

  return figures

