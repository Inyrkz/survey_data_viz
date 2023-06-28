# import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
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

        if j == "Open-ended":
            open_ended.append(i)
        elif j == "Scaling":
            categorical.append(i)
        elif j == "Multichoice":
            categorical.append(i)
        # REMEMBER: TEST THIS PROFILING SECTION LATER WHEN YOU GET MORE SURVEY DATA***
        elif j == "Profiling":
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

        # Plot charts based on category
        plot_charts(categorized_questions.get('categorical'),
                    categorized_questions.get('numeric'),
                    df,
                    storage_path)

        # send the image files
        return jsonify({'charts': charts})


# COMPLETE LATER
class Analysis(Resource):
    def get(self):
        df = pd.read_csv(request.files.get("survey_data"))
        df_meta = pd.read_csv(request.files.get("survey_metadata"))
        # survey_id = request.form.get("survey_id")
        # responses len(df)
        # completeness rate
        # average response **GET FROM SURVEY METADATA
        # invalid responses **WHAT IS THIS?
        # profanities
        return jsonify({'responses': len(df),
                        'completeness_rate': "",
                        'average_responses': "",
                        'invalid_responses': "",
                        'profanities': ""})


# add ChartResource to the API
api.add_resource(ChartResource, '/charts')
api.add_resource(Analysis, '/analysis')

if __name__ == '__main__':
    app.run(debug=True)
