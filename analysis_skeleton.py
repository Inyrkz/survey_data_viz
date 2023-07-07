import numpy as np
import pandas as pd
import requests
# from profanity_check import predict
from seaborn_plot_functions import *

# create empty lists for the different categories of survey questions
categorical = []
numeric = []
open_ended = []
others = []
# create a list to store all the charts
charts = []


# SECTION 1: Read and Parse the survey data
# The survey data will be gotten from a link
def read_survey(url):
    """Function to get and parse the survey data from URL.
    Note, the URL will be extracted from the post request sent to our API.

    :parameter
    url: str,
        This is the URL to get the data.

    :return
    df: DataFrame
        Data Frame containing the survey data for analysis
    """
    response = requests.get(url)
    # check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        return f'Error: Failed to retrieve data from the URL. Status code: {response.status_code}'


# Section 2: Categorize the Survey Questions
def categorize_survey_questions(df, df_meta):
    """Function to categorize the survey question

    Categorical - For scaling questions and multichoice questions. Also if the question is a profiling question
        (eg., gender & country), check if it is categorical, then add it to this group.
    Numeric - If the profiling question (eg., age) is of type integer or float, add it to the numeric group.
    Open_ended - If the question is an open ended question, add it to this group.
        Sentiment analysis will be carried out later, as well as entity extraction.
    Other - for unknown categories and edge cases.

    Parameters
    ---------
    df: A dataframe,
        This is the survey data
    df_meta: A dataframe,
        This is the survey metadata.

    Return
    ------
    A dictionary with the different categories.
    """
    # threshold to determine if a profiling question is a categorical variable
    cardinality_threshold = 11
    # the total number of survey response. Equivalent to the total number of rows.
    total_responses = len(df)

    # loop through the survey meta data to sort the question.
    for index, rows in df_meta.iterrows():
        i = rows["Questions"]
        j = rows["Tag"]

        if j == "open_ended":
            open_ended.append(i)
        elif j == "scaling":
            categorical.append(i)
        elif j == "multiple_choice":
            categorical.append(i)
        # REMEMBER: TEST THIS PROFILING SECTION LATER WHEN YOU GET MORE SURVEY DATA***
        elif j == "profiling":
            # check the survey dataframe to know if the answer has numerical data
            if df[i].dtype == "float64" or df[i].dtype == "int64":
                numeric.append(i)
            # check the survey dataframe to know if the question is either categorical
            # that is, the number of distinct value is less than the threshold
            # and is not equal to the total_responses.
            elif df[i].nunique() < cardinality_threshold and df[i].nunique() != total_responses:
                categorical.append(i)
        # catch edge cases
        else:
            others.append(i)

    return {'categorical': categorical,
            'numeric': numeric,
            'open_ended': open_ended,
            'others': others}


# # THERE SHOULD BE ANOTHER SECTION HERE TO CORRECT &
# EXTRACT THE SENTIMENTS OF EACH OPEN ENDED QUESTION
# THEN STORE THE RESULT IN A NEW COLUMN


# SECTION 4: Plot Data Based on Category
def plot_charts(categorical_variables, numeric_variables, df, storage_path):
    """Function to plot charts based on the category of the survey question

    Parameters
    ----------
    categorical_variables, list
        This contains all the categorical variable in the survey.
    numeric_variables, list
        This contains all the numeric variable in the survey.
    df, dataframe
        This is the survey data
    storage_path, str
        This is where the directory plotted images will be stored


    """
    # Convert the datatype of all the column in the categorical list to the categorical datatype
    for i in categorical_variables:
        df[i] = df[i].astype('category')

    # if categorical list is not empty, plot bar graphs & pie charts.
    if len(categorical_variables) != 0:
        for column in categorical_variables:
            charts.append(create_bar_graph(series=df[column],
                                           title=column,
                                           storage_path=storage_path))
            charts.append(create_pie_chart(series=df[column],
                                           title=column,
                                           storage_path=storage_path))

    # if numeric list is not empty, plot histogram, boxplot and violin plot graphs.
    if len(numeric_variables) != 0:
        for column in numeric_variables:
            charts.append(create_histogram(data=df[column],
                                           title=column,
                                           storage_path=storage_path))
            charts.append(create_violin_plot(data=df[column],
                                             title=column,
                                             storage_path=storage_path))
            charts.append(create_box_plot(data=df[column],
                                          title=column,
                                          storage_path=storage_path))


# Section 5: Analysis Functions
def average_response_time(survey_dataframe):
    """Function to calculate the average time it took all the responders to fill the survey form

    Parameters
    ----------
    survey_dataframe, dataframe
        This is the survey dataframe. One of the column is 'average_response'

    Return
    ------
    average, float
    """
    column_name = 'average_response_time'
    if column_name not in survey_dataframe.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    average = survey_dataframe[column_name].mean()
    return average


def calculate_completion_percentage(survey_dataframe):
    """Function to calculate the completion rate of a survey response

    Parameters
    ----------
    survey_dataframe, dataframe
        This is the survey dataframe.

    Return
    ------
    completion_percentage, float
    """
    total_cells = survey_dataframe.size
    missing_cells = survey_dataframe.isnull().sum().sum()

    completion_percentage = 100 - (missing_cells / total_cells * 100)
    completion_percentage = round(completion_percentage, 2)
    return completion_percentage


def count_invalid_responses(survey_dataframe, invalid_values=['N/A', 'Unknown']):
    """Function to get the number of invalid responses in a survey.
    Some examples are ['N/A', 'Unknown']

        Parameters
        ----------
        survey_dataframe, dataframe
            This is the survey dataframe.
        invalid_values, list
            This contains the invalid values. The default value is ['N/A', 'Unknown'].

        Return
        ------
        invalid_responses, int
        """
    invalid_responses = survey_dataframe[survey_dataframe.isin(invalid_values)].count().sum()
    return invalid_responses


# def count_profanities(survey_dataframe, text_columns=open_ended):
#     """Function to get the number of invalid responses in a survey.
#     Some examples are ['N/A', 'Unknown']
#
#     Parameters
#     ----------
#     survey_dataframe, dataframe
#         This is the survey dataframe.
#     text_columns, list
#         This contains the list of coumns to check. The default is the open_ended question list
#
#     Return
#     ------
#        count, int
#     """
#     count = 0
#     if len(text_columns) != 0:
#         # Iterate over the specified text columns
#         for column in text_columns:
#             # Iterate over the rows of the DataFrame
#             for _, row in survey_dataframe.iterrows():
#                 text = str(row[column])
#                 # if text is not a missing value, continue
#                 if text == np.nan:
#                     continue
#                 else:
#                     # Use the profanity-check library to predict profanity
#                     profanity_prediction = predict([text])
#
#                     # If profanity is detected, increment the count
#                     if profanity_prediction[0] == 1:
#                         count += 1
#
#     return count
