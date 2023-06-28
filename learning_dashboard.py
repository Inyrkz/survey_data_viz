"""I'm using this to learn and practice Dash"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go



# create dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Simple Web Dashboard"),
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Pie(
                        labels=["Category 1", "Category 2", "Category 3"],
                        values=[30, 40, 30],
                        marker=dict(colors=['#ff7f0e', '#1f77b4', '#2ca02c']),
                        textinfo='label+percent'
                    )
                ],
                layout=go.Layout(title="Pie Chart")
            )
        ),
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=["Category 1", "Category 2", "Category 3"],
                        y=[10, 20, 30],
                        marker=dict(color='#1f77b4')
                    )
                ],
                layout=go.Layout(title="Bar Graph")
            )
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
