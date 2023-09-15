"""This script contains logic.
This is the engine of the project."""


# from profanity_check import predict
import pandas as pd
from textblob import TextBlob
from seaborn_plot_functions import *
from analysis_functions import * 


# SECTION 1: Read and Parse the survey data
# The survey data will be gotten from a link
def parse_quest_data(df, df_meta):
    """Function to get and parse the survey data from URL.
    Note, the URL will be extracted from the post request sent to our API.

    :parameter
    quest_data_df: DataFrame,
        This is the dataframe to get the quest survey data.
    quest_metadata_df: DataFrame,
        This is the dataframe to get the quest survey metadata.

    :return
    restructured_df: DataFrame
        The quest survey data for analysis
    metadata_df; DataFrame
        The metadata showing the unique questions and the question type

    """
    # Merge the two DataFrames based on the survey_item_id
    merged_df = df.merge(df_meta, left_on='survey_item_id', right_on='id')

    # Extract a metadata dataframe as one of the output
    metadata_df = merged_df[['question', 'type', 'survey_item_id']]
    # drop duplicates in the metadata_df, if any.
    metadata_df = metadata_df.drop_duplicates()
        
    # Extract a response metadata
    response_metadata = merged_df[['response_id', 'quest_completion_time', 'city',
                                   'country', 'region', 'latitude', 'longitude']]
    # drop duplicates in the response_metadata, if any.
    response_metadata = response_metadata.drop_duplicates()
        
    # Keep only a subset of the data. The question and the response
    # created_at shows the individual responses based on the time survey was taken
    merged_df = merged_df[['question', 'response', 'created_at']]
    merged_df.drop_duplicates(inplace=True)
    
    # Use pivot to restructure the data
    # Use 'created at' to get the individual response to all the questions
    restructured_df = merged_df.pivot(index='created_at', columns='question')
    # Flatten the column index by joining the levels with underscore
    restructured_df.columns = ['_'.join(col) for col in restructured_df.columns]
    # Remove the 'response_' prefix from the column names
    restructured_df.columns = [col.replace('response_', '') for col in restructured_df.columns]
    return restructured_df, metadata_df, response_metadata


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
    # create empty lists for the different categories of survey questions
    categorical = []
    numeric = []
    open_ended = []
    others = []

    # threshold to determine if a profiling question is a categorical variable
    cardinality_threshold = 11
    # the total number of survey response. Equivalent to the total number of rows.
    total_responses = len(df)

    # loop through the survey meta data to sort the question.
    for index, rows in df_meta.iterrows():
        i = rows["question"]
        j = rows["type"]

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

# Section 3: Text Correction
def correct_text(df, columns_to_correct):
    """Function to correct response to open_ended responses.

    Parameters
    ----------
    df: Pandas DataFrame
        This is the dataframe with the quest survey responses.
    columns_to_correct: list
        It is a list of column names to perform text correction on.

    Returns
    -------
    df : Pandas DataFrame
        The DataFrame with corrected text values.
    """
    # Iterate over the columns
    for column in columns_to_correct:
        # Apply the text correction operation using TextBlob if row isn't missing
        df[column] = df[column].apply(lambda x: str(TextBlob(x).correct()) if not pd.isna(x) else x)
    return df


# section 4: Sentiment Analysis
def perform_sentiment_analysis(df, columns_to_analyze):
    """Function to perform sentiment analysis on specified columns of a DataFrame and categorize the sentiment.
    This works with the 'categorize_sentiment' function.

    Parameters
    ----------
    df : Pandas DataFrame
        The DataFrame containing the columns to analyze.
    columns_to_analyze : list
        List of column names to perform sentiment analysis on.

    Returns
    -------
    df : Pandas DataFrame
        The DataFrame with the sentiment analysis results added as new columns.
    sentiment_columns: list
        This is a list of the sentiment columns for plotting
    """
    sentiment_columns = []
    for column in columns_to_analyze:
        new_column = column + "_sentiment"
        sentiment_columns.append(new_column)
        df[new_column] = df[column].apply(
            lambda x: categorize_sentiment(TextBlob(str(x)).sentiment.polarity) if not pd.isna(x) else x)

    return df, sentiment_columns


def categorize_sentiment(polarity):
    """Function to categorize sentiment polarity into positive, neutral, or negative.

    Parameters
    ----------
    polarity : float
        The sentiment polarity value ranging from -1 to 1.

    Returns
    -------
    category : str
        The sentiment category (positive, neutral, or negative).
    """
    if polarity > 0.3:
        category = "positive"
    elif polarity > -0.3:
        category = "neutral"
    else:
        category = "negative"

    return category


def get_quest_id(df_meta, column):
    """Function to get the corresponding quest_id based on the quest question

    Parameters
    ----------
    df_meta: Pandas DataFrame
        This is the dataframe with the quest survey metadata.
    column: list
        It is a list of column containing the question whose id you want to get.

    Returns
    -------
    quest_id: str
        The unique quest_id of the quest survey question."""
    matching_rows = df_meta.loc[df_meta['question'] == column, 'survey_item_id']
    if not matching_rows.empty:
        quest_id = str(matching_rows.iloc[0])
        # Rest of your code using quest_id
    else:
        # Handle the case when there are no matching rows
        quest_id = None  # or assign a default value or raise an exception
    return quest_id


# # SECTION 4: Plot Data Based on Category
# def plot_charts(categorical_variables, sentiment_columns, numeric_variables, open_questions, df, df_meta, storage_path):
#     """Function to plot charts based on the category of the survey question

#     Parameters
#     ----------
#     categorical_variables: list
#         This contains all the categorical variable in the survey.
#     sentiment_columns: list
#         This contains all the sentiments of open_ended question categories.
#     numeric_variables: list
#         This contains all the numeric variable in the survey.
#     open_questions: list
#         This contains all the open ended questions in the survey.
#     df: dataframe
#         This is the quest survey data
#     df_meta: dataframe
#         The quest survey metadata
#     storage_path: str
#         This is where the directory plotted images will be stored
#     """
#     # create a list to store all the charts
#     charts = []

#     # Convert the datatype of all the column in the categorical list to the categorical datatype
#     for i in categorical_variables:
#         df[i] = df[i].astype('category')

#     # if categorical list is not empty, plot bar graphs & pie charts.
#     if len(categorical_variables) != 0:
#         for column in categorical_variables:
#             quest_id = get_quest_id(df_meta, column)
#             charts.append(create_bar_graph(series=df[column],
#                                            title=column,
#                                            survey_item_id=quest_id,
#                                            storage_path=storage_path))
#             charts.append(create_pie_chart(series=df[column],
#                                            title=column,
#                                            survey_item_id=quest_id,
#                                            storage_path=storage_path))

#     # if sentiment_columns list is not empty, plot bar graphs & pie charts.
#     if len(sentiment_columns) != 0:
#         for column in sentiment_columns:
#             # remove the '_sentiment' from column name to get the original column & quest_id
#             quest_id = get_quest_id(df_meta, column[:-10])
#             charts.append(create_bar_graph(series=df[column],
#                                            title=column,
#                                            survey_item_id=quest_id,
#                                            storage_path=storage_path))
#             # charts.append(create_pie_chart(series=df[column],
#             #                                title=column,
#             #                                survey_item_id=quest_id,
#             #                                storage_path=storage_path))

#     # if numeric list is not empty, plot histogram, boxplot and violin plot graphs.
#     if len(numeric_variables) != 0:
#         for column in numeric_variables:
#             quest_id = get_quest_id(df_meta, column)
#             charts.append(create_histogram(data=df[column],
#                                            title=column,
#                                            survey_item_id=quest_id,
#                                            storage_path=storage_path))
#             charts.append(create_violin_plot(data=df[column],
#                                              title=column,
#                                              survey_item_id=quest_id,
#                                              storage_path=storage_path))
#             charts.append(create_box_plot(data=df[column],
#                                           title=column,
#                                           survey_item_id=quest_id,
#                                           storage_path=storage_path))

#     # if there are open_questions, plot wordcloud
#     if len(open_questions) != 0:
#         for column in open_questions:
#             # Get the quest_item_id
#             quest_id = get_quest_id(df_meta, column)
#             # add wordcloud to the charts
#             charts.append(create_wordcloud(data=df[column],
#                                            title=column,
#                                            survey_item_id=quest_id,
#                                            storage_path=storage_path))

#     return charts




# SECTION 4 Revamped: Plot Data Based on Category
def compute_charts_data(categorical_variables, sentiment_columns, 
                        numeric_variables, open_questions, df, df_meta, response_metadata):
    """Function to compute charts data based on the category of the survey question

    Parameters
    ----------
    categorical_variables: list
        This contains all the categorical variable in the survey.
    sentiment_columns: list
        This contains all the sentiments of open_ended question categories.
    numeric_variables: list
        This contains all the numeric variable in the survey.
    open_questions: list
        This contains all the open ended questions in the survey.
    df: dataframe
        This is the quest survey data
    df_meta: dataframe
        The quest survey metadata
    response_metadata: dataframe
        The quest response metadata
    """
    # create a list to store all the charts
    charts = []

    # compute line chart for daily response
    charts.append(get_daily_response_count_data(df))

    # compute chart for distribution of respondent by city
    charts.append(analyze_city(response_metadata))

    # compute chart for distribution of respondent by country
    charts.append(analyze_country(response_metadata))

    # compute chart for distribution of respondent by region
    charts.append(analyze_region(response_metadata))

    # Convert the datatype of all the column in the categorical list to the categorical datatype
    for i in categorical_variables:
        df[i] = df[i].astype('category')

    # if categorical list is not empty, plot bar graphs & pie charts.
    if len(categorical_variables) != 0:
        for column in categorical_variables:
            quest_id = get_quest_id(df_meta, column)
            charts.append(compute_bar_graph_data(series=df[column],
                                           title=column,
                                           survey_item_id=quest_id))
            charts.append(compute_pie_chart_data(series=df[column],
                                           title=column,
                                           survey_item_id=quest_id))

    # if sentiment_columns list is not empty, plot bar graphs & pie charts.
    if len(sentiment_columns) != 0:
        for column in sentiment_columns:
            # remove the '_sentiment' from column name to get the original column & quest_id
            quest_id = get_quest_id(df_meta, column[:-10])
            charts.append(compute_bar_graph_data(series=df[column],
                                           title=column,
                                           survey_item_id=quest_id))
            # charts.append(compute_pie_chart_data(series=df[column],
            #                                title=column,
            #                                survey_item_id=quest_id))

    # if numeric list is not empty, plot histogram, boxplot and violin plot graphs.
    if len(numeric_variables) != 0:
        for column in numeric_variables:
            quest_id = get_quest_id(df_meta, column)
            charts.append(compute_histogram_data(data=df[column],
                                                 title=column,
                                                 survey_item_id=quest_id))
            charts.append(compute_violin_plot_data(data=df[column],
                                                   title=column,
                                                   survey_item_id=quest_id))
            charts.append(compute_box_plot_data(data=df[column],
                                                title=column,
                                                survey_item_id=quest_id))

    # if there are open_questions, plot wordcloud
    if len(open_questions) != 0:
        for column in open_questions:
            # Get the quest_item_id
            quest_id = get_quest_id(df_meta, column)
            # add wordcloud to the charts
            charts.append(compute_wordcloud_data(data=df[column],
                                           title=column,
                                           survey_item_id=quest_id))

    return charts


# Section 5: GeoJSON Data
def create_geojson(response_metadata, id_field, latitude_field, longitude_field):
    """
    Create a GeoJSON FeatureCollection from a DataFrame containing latitude, longitude, and an identifier field.

    Parameters:
        response_metadata (pd.DataFrame): The DataFrame containing the data.
        id_field (str): The name of the identifier field (e.g., response_id).
        latitude_field (str): The name of the latitude field.
        longitude_field (str): The name of the longitude field.

    Returns:
        str: A GeoJSON FeatureCollection as a JSON string.
    """
    # Create a list of GeoJSON features
    features = []
    for index, row in response_metadata.iterrows():
        feature = {
            "type": "Feature",
            "properties": {
                id_field: row[id_field]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row[longitude_field], row[latitude_field]]
            }
        }
        features.append(feature)

    # Create a GeoJSON FeatureCollection
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson_data


# Section 6: Analysis Functions
def average_response_time(response_metadata):
    """Function to calculate the average time it took all the responders to fill the survey form

    Parameters
    ----------
    response_metadata: dataframe
        This is the survey dataframe. One of the column is 'average_response'

    Return
    ------
    average: float
    """
    column_name = 'quest_completion_time'
    if column_name not in response_metadata.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    average = response_metadata[column_name].mean()
    return average


def calculate_completion_percentage(survey_dataframe):
    """Function to calculate the completion rate of a survey response

    Parameters
    ----------
    survey_dataframe: dataframe
        This is the survey dataframe.

    Return
    ------
    completion_percentage: float
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
    survey_dataframe: dataframe
        This is the survey dataframe.
    invalid_values: list
        This contains the invalid values. The default value is ['N/A', 'Unknown'].

    Return
    ------
    invalid_responses: int
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
#         This contains the list of columns to check. The default is the open_ended question list
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
