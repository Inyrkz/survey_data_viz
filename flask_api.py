from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from analysis_skeleton import *

# create Flask app and initialize the REST API
app = Flask(__name__)
api = Api(app)


class ChartResource(Resource):
    def post(self):
        # Access the uploaded files
        # quest_data, quest_metadata and survey_id are the key names from the client
        quest_data = pd.read_csv(request.files.get("quest_data"))
        quest_metadata = pd.read_csv(request.files.get("quest_metadata"))
        quest_id = request.form.get("quest_id")

        # read quest survey data and metadata
        df, df_meta, response_meta = parse_quest_data(quest_data, quest_metadata)
        # Generate storage path based on survey id
        storage_path = create_storage_path(str(quest_id))
        # Categorize survey questions
        categorized_questions = categorize_survey_questions(df, df_meta)

        # Perform Quick Analysis
        # profanity_count = count_profanities(survey_dataframe=df,
        #                                     text_columns=categorized_questions.get('open_ended'))
        invalid_response_count = count_invalid_responses(survey_dataframe=df)
        completion_rate = calculate_completion_percentage(survey_dataframe=df)
        average_quest_completion_time = average_response_time(response_metadata=response_meta)

        # correct texts in open_ended questions
        df = correct_text(df=df,
                          columns_to_correct=categorized_questions.get('open_ended'))
        # perform sentiment analysis
        df, sentiment_columns = perform_sentiment_analysis(df=df,
                                                           columns_to_analyze=categorized_questions.get('open_ended'))

        # Plot charts based on category
        charts = compute_charts_data(categorized_questions.get('categorical'),
                                     sentiment_columns,
                                     categorized_questions.get('numeric'),
                                     categorized_questions.get('open_ended'),
                                     df,
                                     df_meta,
                                     response_meta
                                    )

        # send the image files
        return jsonify({'quest_id': str(quest_id),
                        'analysis_result': {'number of responses': str(len(df)),
                                            'average_quest_completion_time': str(average_quest_completion_time),
                                            'completeness_rate': str(completion_rate),
                                            'average_responses': "",
                                            'invalid_responses': str(invalid_response_count),
                                            'profanities': "Unknown"},
                        'charts': charts})


# add ChartResource to the API
api.add_resource(ChartResource, '/charts')


if __name__ == '__main__':
    app.run(debug=True)
