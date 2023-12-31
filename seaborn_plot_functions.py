"""This script contains functions to create different kinds of plot with Seaborn"""
import boto3
from botocore import exceptions as botoException
from urllib3.exceptions import ConnectTimeoutError
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO


# Save the generated plot to AWS S3 bucket


aws_s3 = boto3.client(
    "s3",
    aws_access_key_id=MY_AWS_ACCESS_KEY_ID,
    aws_secret_access_key=MY_AWS_SECRET_ACCESS_KEY,
    region_name=MY_AWS_REGION_NAME
)

s3_base_url = ""


def save_to_s3(file, file_key):
    """Convert the matplotlib figure to bytes,
    upload it to an S3 bucket with the specified key,
    and returns the URL of the uploaded image."""
    # convert the file to bytes
    buffer = BytesIO()
    extension = "png"
    file.savefig(buffer, format=extension)
    # set the stream position to the beginning of the buffer.
    buffer.seek(0)
    # upload the file to s3
    # Construct the object key with the desired folder path
    object_key = f"{folder_path}/{file_key}.{extension}"

    try:
        aws_s3.upload_fileobj(buffer, s3_bucket_name, object_key)
        return s3_base_url + object_key
    except botoException.ConnectTimeoutError as bctr:
        print("Boto time out exception" + str(bctr))
    except ConnectTimeoutError as ctr:
        print("URL LIB time out exception" + str(ctr))
    except Exception as e:
        print("Error uploading to s3" + str(e))

    return None


def create_storage_path(survey_id="sample_001"):
    """Function to create a path in the directory based on the unique survey id.

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
    """Function to create a bar graph.

    Parameters
    ----------
    series: Pandas Series.
        It will take the unique values and their total count
    title: str,
        Title of the plot. Let this be the column name
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str,
        default value is "Values"
    y_label: str,
        default value is "Count"
    """
    # set the plot background style
    sns.set(style="white")
    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    # get the unique values and their total count
    value_counts = series.value_counts()
    # create a bar graph
    ax = sns.barplot(x=value_counts.index, y=value_counts.values, color='brown')
    # set the labels and the title
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    # Add value labels to the bars
    for bar in ax.patches:
        # Get the coordinates of the bar
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        # Add the text label
        ax.text(x, y, int(y), ha='center', va='bottom')
    # plt.show()
    # Save the chart as an image. Let the image match the title
    # replace spaces in the title with _ and ? with an empty string
    filename = '{}_bar_chart.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    # plt.savefig(full_path)
    # return full_path
    # Replace the local file saving with S3 upload
    url = save_to_s3(plt, full_path)
    return url


def create_violin_plot(data, title, storage_path, x_label=" ", y_label="Value"):
    """Function to create a violin plot.

    Parameters
    ----------
    data: Pandas Series.
        It will take the unique values and their total count
    title: str,
        title of the plot. Let this be the column name
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str,
        default value is ""
    y_label: str,
        default value is "Value"
    """
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 4))  # Adjust the figure size as needed
    # plot violin plot
    ax = sns.violinplot(data=data)
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    # plt.show()
    filename = '{}_violin_chart.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    # plt.savefig(full_path)
    # return full_path

    # Replace the local file saving with S3 upload
    url = save_to_s3(plt, full_path)
    return url


def create_box_plot(data, title, storage_path, x_label=" ", y_label="Value"):
    """Function to create a box plot.

    Parameters
    ----------
    data: Pandas Series.
        It will take the unique values and their total count
    title: str, title of the plot.
        Let this be the column name
    storage_path: str
        Path to store the image plots based on the unique survey_id
    x_label: str,
        default value is ""
    y_label: str,
        default value is "Value"
    """
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 4))  # Adjust the figure size as needed
    # plot boxplot
    ax = sns.boxplot(data=data)
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    # plt.show()
    filename = '{}_boxplot.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    # plt.savefig(full_path)
    # return full_path

    # Replace the local file saving with S3 upload
    url = save_to_s3(plt, full_path)
    return url


def create_pie_chart(series, title, storage_path):
    """Function to create a pie chart

    Parameters
    ----------
    series: Pandas Series.
        It will take the unique values and their total count
    title: str,
        Title of the plot. Let this be the column name
    storage_path: str
        Path to store the image plots based on the unique survey_id
    """
    value_counts = series.value_counts()
    # Get the labels and sizes as a list
    labels = value_counts.index.tolist()
    sizes = value_counts.values.tolist()
    plt.figure(figsize=(6, 6))  # Adjust the figure size as needed
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title(title)
    # plt.show()
    # Save the chart as an image. Let the image match the title
    filename = '{}_pie_chart.png'.format(title.replace(" ", "_").replace("?", ""))
    # add the image plot to the survey folder
    full_path = os.path.join(storage_path, filename)
    # plt.savefig(full_path)
    # return full_path

    # Replace the local file saving with S3 upload
    url = save_to_s3(plt, full_path)
    return url


def create_histogram(data, title, storage_path, x_label="Values", y_label="Frequency", bins="auto"):
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
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    ax = sns.histplot(data, bins=bins)
    ax.set(xlabel=x_label, ylabel=y_label, title=title)
    # Save the chart as an image. Let the image match the title
    filename = '{}_histogram.png'.format(title.replace(" ", "_").replace("?", ""))
    full_path = os.path.join(storage_path, filename)
    # plt.savefig(full_path)
    # return full_path
    # Replace the local file saving with S3 upload
    url = save_to_s3(plt, full_path)
    return url
