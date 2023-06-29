import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import joblib
from profanity_check import predict
from plotly_plot_functions import create_bar_graph, create_violin_plot, create_storage_path
from plotly_plot_functions import create_box_plot, create_pie_chart, create_histogram

# create Flask app and initialize the REST API
app = Flask(__name__)
api = Api(app)

# create empty lists for the different categories of survey questions
categorical = []
numeric = []
open_ended = []
others = []
# create a list to store all the charts
charts = []


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
    """Function to plot charts based on the category of the survey question"""
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
    column_name = 'average_response'
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


def count_profanities(survey_dataframe, text_columns=open_ended):
    """Function to get the number of invalid responses in a survey.
    Some examples are ['N/A', 'Unknown']

    Parameters
    ----------
    survey_dataframe, dataframe
        This is the survey dataframe.
    text_columns, list
        This contains the list of coumns to check. The default is the open_ended question list

    Return
    ------
       count, int
    """
    count = 0
    if len(text_columns) != 0:
        # Iterate over the specified text columns
        for column in text_columns:
            # Iterate over the rows of the DataFrame
            for _, row in survey_dataframe.iterrows():
                text = str(row[column])
                # if text is not a missing value, continue
                if text != np.nan():
                    # Use the profanity-check library to predict profanity
                    profanity_prediction = predict([text])

                    # If profanity is detected, increment the count
                    if profanity_prediction[0] == 1:
                        count += 1
                else:
                    continue

    return count



class ChartResource(Resource):
    def post(self):
        # Access the uploaded files
        # survey_data, survey_metadata and survey_id are the key names from the client
        df = pd.read_csv(request.files.get("survey_data"))
        df_meta = pd.read_csv(request.files.get("survey_metadata"))
        survey_id = request.form.get("survey_id")

        # Generate storage path based on survey id
        storage_path = create_storage_path(str(survey_id))

        # Categorize survey questions
        categorized_questions = categorize_survey_questions(df, df_meta)

        # Perform Quick Analysis
        profanity_count = count_profanities(survey_dataframe=df,
                                            text_columns=categorized_questions.get('open_ended'))
        invalid_response_count = count_invalid_responses(survey_dataframe=df)
        completion_perc = calculate_completion_percentage(survey_dataframe=df)
        average_time = average_response_time(survey_dataframe=df)

        # Plot charts based on category
        plot_charts(categorized_questions.get('categorical'),
                    categorized_questions.get('numeric'),
                    df,
                    storage_path)

        # send the image files
        return jsonify({'survey_id': survey_id,
                        'analysis': {'number of responses': len(df),
                                     'completeness_rate': completion_perc,
                                     'average_responses': average_time,
                                     'invalid_responses': invalid_response_count,
                                     'profanities': profanity_count},
                        'charts': charts,
                        })


# add ChartResource to the API
api.add_resource(ChartResource, '/charts')


if __name__ == '__main__':
    app.run(debug=True)
