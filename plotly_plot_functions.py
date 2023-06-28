"""This script contains functions to create different kinds of plot"""

# import matplotlib.pyplot as plt
# import seaborn as sns
import plotly.graph_objs as go
import os
# import plotly.offline as pyo
# import plotly.io as pio


def create_storage_path(survey_id="sample_001"):
    """Fuction to create a path in the directory based on the unique survey id.

    :param survey_id: str
                The survey id

    :return: full_path: str
                The full path to where the plots will be stored
    """
    # create a directory to store the plot images
    directory_path = 'survey_images'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    # create a folder for each survey to store the charts associated with that survey
    storage_path = os.path.join(directory_path, survey_id)
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path


def create_bar_graph(series, title, storage_path, x_label="Values", y_label="Count"):
    """
    Function to create a bar graph.

    Parameters
    ----------
    series: Pandas Series
        Series containing the unique values and their total count.
    title: str
        Title of the plot.
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str, optional
        Label for the x-axis, default is "Values".
    y_label: str, optional
        Label for the y-axis, default is "Count".
    """
    value_counts = series.value_counts()
    fig = go.Figure(data=[go.Bar(x=value_counts.index, y=value_counts.values)])
    fig.update_layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label)
    )
    # pio.show(fig)
    # Save the chart as an image. Let the image match the title
    # replace spaces in the title with _ and ? with an empty string
    filename = '{}_bar_chart.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    fig.write_image(full_path)
    return full_path


def create_violin_plot(data, title, storage_path, x_label="Chart", y_label="Value"):
    """
    Function to create a violin plot.

    Parameters
    ----------
    data: Pandas Series
        Series containing the data for the violin plot.
    title: str
        Title of the plot.
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str, optional
        Label for the x-axis, default is an empty string.
    y_label: str, optional
        Label for the y-axis, default is "Value".
    """
    fig = go.Figure(data=go.Violin(y=data))

    fig.update_layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label)
    )
    # pio.show(fig)
    # Save the chart as an image. Let the image match the title
    # replace spaces in the title with _
    filename = '{}_violin_chart.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    fig.write_image(full_path)
    return full_path


def create_box_plot(data, title, storage_path, x_label="Chart", y_label="Value"):
    """
    Function to create a box plot.

    Parameters
    ----------
    data: Pandas Series
        Series containing the data for the box plot.
    title: str
        Title of the plot.
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str, optional
        Label for the x-axis, default is an empty string.
    y_label: str, optional
        Label for the y-axis, default is "Value".
    """
    fig = go.Figure(data=go.Box(y=data))

    fig.update_layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label)
    )

    # pio.show(fig)
    # Save the chart as an image. Let the image match the title
    filename = '{}_violin_plot.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    fig.write_image(full_path)
    return full_path


def create_pie_chart(series, title, storage_path):
    """
    Function to create a pie chart.

    Parameters
    ----------
    series: Pandas Series
        Series containing the unique values and their total count.
    title: str
        Title of the plot.
    storage_path: str
        Path to store the image plots based on the unique survey_id
    """
    value_counts = series.value_counts()
    fig = go.Figure(data=[go.Pie(labels=value_counts.index,
                                 values=value_counts.values)])
    fig.update_layout(title=title)
    # pio.show(fig)
    # Save the chart as an image. Let the image match the title
    filename = '{}_pie_chart.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    fig.write_image(full_path)
    return full_path


def create_histogram(data, title, storage_path, x_label="Values", y_label="Frequency", bins=None):
    """
    Function to create a histogram.

    Parameters
    ----------
    data: Pandas Series or numpy array
        Data to plot the histogram.
    title: str
        Title of the plot.
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str, optional
        Label for the x-axis, default is "Values".
    y_label: str, optional
        Label for the y-axis, default is "Frequency".
    bins: int, optional
        Number of histogram bins, default is None (automatically determined).
    """
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=data, nbinsx=bins))
    fig.update_layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label)
    )
    # pio.show(fig)
    # Save the chart as an image. Let the image match the title
    filename = '{}_histogram.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    fig.write_image(full_path)
    return full_path
