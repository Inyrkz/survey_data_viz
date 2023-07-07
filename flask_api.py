import pandas as pd
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from analysis_skeleton import *

# create Flask app and initialize the REST API
app = Flask(__name__)
api = Api(app)


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
        # profanity_count = count_profanities(survey_dataframe=df,
        #                                     text_columns=categorized_questions.get('open_ended'))
        invalid_response_count = count_invalid_responses(survey_dataframe=df)
        completion_perc = calculate_completion_percentage(survey_dataframe=df)
        average_time = average_response_time(survey_dataframe=df)

        # Plot charts based on category
        plot_charts(categorized_questions.get('categorical'),
                    categorized_questions.get('numeric'),
                    df,
                    storage_path)

        # send the image files
        return jsonify({'survey_id': str(survey_id),
                        'analysis_result': {'number of responses': str(len(df)),
                                            'completeness_rate': str(completion_perc),
                                            'average_responses': str(average_time),
                                            'invalid_responses': str(invalid_response_count),
                                            'profanities': "Unknown"},
                        'charts': charts,
                        'image_format': "PNG"
                        })


# add ChartResource to the API
api.add_resource(ChartResource, '/charts')


if __name__ == '__main__':
    app.run(debug=True)
