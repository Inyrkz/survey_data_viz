"""This script contains functions to create different kinds of plot data. 
The data will be sent to the front-end for plotting.
It is the extension the engine of the project uses.
"""


import pandas as pd
import seaborn as sns
import numpy as np

def compute_bar_graph_data(series, title, survey_item_id):
    """Function to compute data for a bar graph.
    
    Parameters
    ----------
    series: Pandas Series.
        It will take the unique values and their total count
    title: str,
        Title of the plot. Let this be the column name
    survey_item_id: int,
        id associated with the quest survey question    
    """
    value_counts = series.value_counts()
    data = {
        'x_values': value_counts.index.tolist(),
        'y_values': value_counts.values.tolist(),
        'x_label': 'Values',
        'y_label': 'Count',
        'title': title,
        'survey_item_id':survey_item_id,
        'plot_type': ['bar_graph', 'horizontal_bar_graph']
    }
    return data


def compute_pie_chart_data(series, title, survey_item_id):
    """Function to compute data for a pie chart.
    
    Parameters
    ----------
    series: Pandas Series.
        It will take the unique values and their total count
    title: str,
        Title of the plot. Let this be the column name
    survey_item_id: int,
        id associated with the quest survey question
    """
    value_counts = series.value_counts()
    labels = value_counts.index.tolist()
    sizes = value_counts.values.tolist()
    data = {
        'labels': labels,
        'sizes': sizes,
        'title': title,
        'survey_item_id': survey_item_id,
        'plot_type': ['pie_chart', 'donut_chart']
    }
    return data


def compute_violin_plot_data(data, title, survey_item_id):
    """Function to compute data for a violin plot.

    Parameters
    ----------
    data: Pandas Series.
        It will take the unique values and their total count
    title: str,
        title of the plot. Let this be the column name
    survey_item_id: int,
        id associated with the quest survey question
    """
    data = {
        'values': data.tolist(),
        'x_label': '',
        'y_label': 'Value',
        'title': title,
        'survey_item_id': survey_item_id,
        'plot_type': ['violin_plot']
    }
    return data


def compute_box_plot_data(data, title, survey_item_id):
    """Function to compute data for a box plot.
    
    Parameters
    ----------
    data: Pandas Series.
        It will take the unique values and their total count
    title: str, title of the plot.
        Let this be the column name
    survey_item_id: int,
        id associated with the quest survey question
    """
    data = {
        'values': data.tolist(),
        'x_label': '',
        'y_label': 'Value',
        'title': title,
        'plot_type': ['boxplot']
    }
    return data


def compute_histogram_data(data, title, survey_item_id):
    """Function to compute data for a histogram.
    
    Parameters
    ----------
    data: Pandas Series or numpy array
        Data to plot the histogram.
    title: str
        Title of the plot.
    survey_item_id: int,
        id associated with the quest survey question
    """
    data = {
        'values': data.tolist(),
        'x_label': 'Values',
        'y_label': 'Frequency',
        'title': title,
        'survey_item_id': survey_item_id,
        'plot_type': ['histogram']
    }
    return data


def compute_wordcloud_data(data, title, survey_item_id):
    """Function to compute data for a word cloud.
    
    Parameters
    ----------
    data: Pandas Series or numpy array
        Data to plot the histogram.
    title: str
        Title of the plot.
    survey_item_id: int,
        id associated with the quest survey question
    """
    text = ' '.join(data.astype(str).tolist())
    # replace nan with empty string
    text = text.replace('nan', '')
    data = {
        'text': text,
        'title': title,
        'survey_item_id': survey_item_id,
        'plot_type': ['wordcloud']
    }
    return data


# Line Chart
def get_daily_response_count_data(df):
    """
    Function to return data points for daily response counts.

    Parameters:
    - df: DataFrame with a 'created_at' column containing datetime values.

    Returns:
    - data: A dictionary containing 'dates' and 'counts' lists.
    """
    # Reset the index and make 'created_at' an actual column
    df.reset_index(inplace=True)

    # Ensure that 'created_at' is in datetime format
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Extract the date as a string from the 'created_at' column
    df['date'] = df['created_at'].dt.strftime('%Y-%m-%d')

    # Group by date and count the number of responses for each day
    daily_counts = df.groupby('date').size().reset_index()

    # Create a dictionary with data points
    data = {
        'plot_type': 'line_chart',
        'dates': daily_counts['date'].tolist(),
        'counts': daily_counts[0].tolist(),
        'title': 'Daily Response Count',
        'xlabel': 'Date',
        'ylabel': 'Response Count'
    }

    return data
 

def analyze_city(dataframe):
    """
    Analyze city data and compute the number of users from each city.

    Parameters:
    - dataframe: DataFrame containing a 'city' column.

    Returns:
    - city_data: A JSON object with 'city' and 'user_count' fields.
    """
    # Drop duplicates based on the entire row
    dataframe.drop_duplicates(subset=None, keep='first', inplace=True)
    
    # Count the number of users for each city
    city_data = dataframe['city'].value_counts().reset_index()
    city_data.columns = ['city', 'user_count']
    
    # Convert to JSON in the desired format
    city_json = {
        'plot_type': 'horizontal_bar_chart',
        'x_label': 'City',
        'y_label': 'Count',
        'title': 'Distribution of Survey Respondents by City.',
        'city': city_data['city'].tolist(),
        'user_count': city_data['user_count'].tolist()
    }
    return city_json


def analyze_country(dataframe):
    """
    Analyze country data and compute the number of users from each country.

    Parameters:
    - dataframe: DataFrame containing a 'country' column.

    Returns:
    - country_data: A JSON object with 'country' and 'user_count' fields.
    """
    # Drop duplicates based on the entire row
    dataframe.drop_duplicates(subset=None, keep='first', inplace=True)
    
    # Count the number of users for each country
    country_data = dataframe['country'].value_counts().reset_index()
    country_data.columns = ['country', 'user_count']
    
    # Convert to JSON in the desired format
    country_json = {
        'plot_type': 'horizontal_bar_chart',
        'x_label': 'Country',
        'y_label': 'Count',
        'title': 'Distribution of Survey Respondents by Country.',
        'country': country_data['country'].tolist(),
        'user_count': country_data['user_count'].tolist()
    }
    return country_json


def analyze_region(dataframe):
    """
    Analyze region data and compute the number of users from each region.

    Parameters:
    - dataframe: DataFrame containing a 'region' column.

    Returns:
    - region_data: A JSON object with 'region' and 'user_count' fields.
    """
    # Drop duplicates based on the entire row
    dataframe.drop_duplicates(subset=None, keep='first', inplace=True)
    
    # Count the number of users for each region
    region_data = dataframe['region'].value_counts().reset_index()
    region_data.columns = ['region', 'user_count']
    
    # Convert to JSON in the desired format
    region_json = {
        'plot_type': 'horizontal_bar_chart',
        'x_label': 'Region',
        'y_label': 'Count',
        'title': 'Distribution of Survey Respondents by Region.',
        'region': region_data['region'].tolist(),
        'user_count': region_data['user_count'].tolist()
    }
    return region_json

