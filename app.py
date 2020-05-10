#!/usr/bin/env python
from plotly.subplots import make_subplots
import pandas as pd
import requests
import json
import plotly
import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from urllib.request import urlopen

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

app.layout = html.Div([

        #ROW 1
        html.Div(
            [
                html.Div(
                    [
                        dcc.Input(id="stock-input",
                                  placeholder='Please insert stock', type="text"),
                        dcc.RadioItems(
                            id="quarterlyoryearly",
                            options=[
                                {'label': 'Quarterly', 'value': 'quarterly'},
                                {'label': 'Yearly', 'value': 'yearly'}
                            ]
                        )
                    ],
                    className="one-third column",style={"margin-top": "20px"}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Stock Financials",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                )
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "15px"},
        ),

        #ROW 2
        html.Div(
            [
                html.Div(
                    [
                        # ROW 2 COLUMN 1 PLAN TO PUT TABS
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                #ROW2 COLUMN2
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="price"), html.P("Price")],
                                    id="liveprice",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="PE_ratio"), html.P("PE Ratio")],
                                    id="pricetoearnings",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="EPS"), html.P("eps")],
                                    id="earningspershare",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="52wkr"), html.P("52 Week Range")],
                                    id="52wkrange",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        #ROW 2 GRAPH
                        html.Div(
                            [dcc.Graph(id="Earnings & Revenue")],
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="ten columns",
                ),
            ],
            className="row flex-display",
        ),
        #ROW 3
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="Financial Health")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="Debt to Equity")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
        #ROW4
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="Profitability")],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [dcc.Graph(id="Solvency & Liquidity")],
                    className="pretty_container six columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    className="back_container",
    style={"display": "flex", "flex-direction": "column","backgroundColor":'#f2f2f2',"margin":'5%'},
)


@app.callback(Output("quarterlyoryearly", "value"),
              [Input("stock-input", "n_submit")],
              [State("quarterlyoryearly", "value")])
def enter_key(n_sub, qoy):
    if n_sub:
        return qoy

@app.callback([dash.dependencies.Output("Earnings & Revenue", "figure"),
               dash.dependencies.Output("Financial Health", "figure"),
               dash.dependencies.Output("Debt to Equity", "figure"),
               dash.dependencies.Output("Profitability", "figure"),
               dash.dependencies.Output("Solvency & Liquidity", "figure"),
               dash.dependencies.Output("price", "children"),
               dash.dependencies.Output("PE_ratio", "children"),
               dash.dependencies.Output("EPS", "children"),
               dash.dependencies.Output("52wkr", "children")],
              [dash.dependencies.Input("quarterlyoryearly", "value")],
              [dash.dependencies.State("stock-input", "value")]
              )
def update_fig(*args):

    if not any(args):
        raise PreventUpdate
    else:
        qoy, ticker = args

        if qoy.lower() == "yearly":
            IS = requests.get(
                "https://financialmodelingprep.com/api/v3/financials/income-statement/" + ticker)
        elif qoy.lower() == "quarterly":
            IS = requests.get(
                "https://financialmodelingprep.com/api/v3/financials/income-statement/" + ticker + "?period=quarter")

        IS = IS.json()
        IS = IS['financials']
        IS = pd.DataFrame.from_dict(IS)
        IS = IS.set_index("date")

        if qoy == "Yearly" or qoy == "yearly" or qoy == "YEARLY":
            BS = requests.get(
                "https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/" + ticker)
        elif qoy == "Quarterly" or qoy == "quarterly" or qoy == "QUARTERLY":
            BS = requests.get(
                "https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/" + ticker + "?period=quarter")

        BS = BS.json()
        BS = BS['financials']
        BS = pd.DataFrame.from_dict(BS)
        BS = BS.set_index("date")

        if qoy == "Yearly" or qoy == "yearly" or qoy == "YEARLY":
            CF = requests.get(
                "https://financialmodelingprep.com/api/v3/financials/cash-flow-statement/" + ticker)
        elif qoy == "Quarterly" or qoy == "quarterly" or qoy == "QUARTERLY":
            CF = requests.get(
                "https://financialmodelingprep.com/api/v3/financials/cash-flow-statement/" + ticker + "?period=quarter")

        CF = CF.json()
        CF = CF['financials']
        CF = pd.DataFrame.from_dict(CF)
        CF = CF.set_index("date")

        df_FS = pd.concat([IS, BS, CF], axis=1, sort=True)
        Date = df_FS.index
        df_FS.fillna(0, inplace=True)

        # EARNINGS & REVENUE
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=Date, y=df_FS['Revenue'],
                                 mode='lines+markers',
                                 name='Revenue'), secondary_y=False, )
        fig.add_trace(go.Bar(x=Date, y=df_FS['Profit Margin'],
                             opacity=0.2,
                             name='Profit Margin'), secondary_y=True, )

        fig.add_trace(go.Scatter(x=Date, y=df_FS['Consolidated Income'],
                                 mode='lines+markers',
                                 name='Earnings'), secondary_y=False, )
        fig.add_trace(go.Scatter(x=Date, y=df_FS['Operating Cash Flow'],
                                 mode='lines+markers',
                                 name='Operating Cash Flow'), secondary_y=False, )
        fig.add_trace(go.Scatter(x=Date, y=df_FS['Free Cash Flow'],
                                 mode='lines+markers',
                                 name='Free Cash Flow'), secondary_y=False, )
        fig.add_trace(go.Scatter(x=Date, y=df_FS['Operating Expenses'],
                                 mode='lines+markers',
                                 name='Operating Expenses'), secondary_y=False, )

        fig.update_layout(title="EARNINGS & REVENUE",
                          barmode='group', hovermode='x',legend_orientation="h",legend=dict(x=0, y=-0.7))
        fig.update_yaxes(title_text="in USD", secondary_y=False)
        fig.update_yaxes(title_text="Profit Margin", secondary_y=True)
        fig.update_xaxes(rangeslider_visible=True)

        # FINANCIAL HEALTH
        colors = ['blue', ] * 4
        colors[1] = 'crimson'
        colors[3] = 'crimson'

        fig2 = go.Figure([go.Bar(
            x=['Current Assets', 'Current Liabilities', 'Non-Current Assets', 'Non-Current Liabilities'],
            y=[df_FS["Total current assets"].iloc[-1], df_FS["Total current liabilities"].iloc[-1],
               df_FS["Total non-current assets"].iloc[-1], df_FS["Total non-current liabilities"].iloc[-1]],
            marker_color=colors
        )])
        fig2.update_layout(title="FINANCIAL HEALTH", barmode='group', hovermode='x', yaxis_title="in USD")
        cols = df_FS.columns
        df_FS[cols] = df_FS[cols].apply(pd.to_numeric, errors='coerce')

        # DEBT TO EQUITY

        df_FS['Debt to Equity'] = (df_FS['Total debt'] / df_FS['Total shareholders equity'])
        df_FS['Debt to Equity'] = df_FS['Debt to Equity'].round(3)

        fig3 = make_subplots(specs=[[{"secondary_y": True}]])

        fig3.add_trace(go.Scatter(x=Date, y=df_FS['Total debt'],
                                  mode='lines+markers',
                                  name='Debt'), secondary_y=False, )
        fig3.add_trace(go.Scatter(x=Date, y=df_FS['Total shareholders equity'],
                                  mode='lines+markers',
                                  name='Total Equity'), secondary_y=False, )
        fig3.add_trace(go.Bar(x=Date, y=df_FS['Debt to Equity'],
                              opacity=0.2,
                              name='Debt to Equity'), secondary_y=True, )
        fig3.add_trace(go.Scatter(x=Date, y=df_FS['Cash and cash equivalents'],
                                  mode='lines+markers',
                                  name='Cash & Cash Equivalents'), secondary_y=False, )

        fig3.update_layout(title="DEBT TO EQUITY",
                           barmode='group', hovermode='x',legend_orientation="h",legend=dict(x=0, y=-0.7))
        fig3.update_yaxes(title_text="in USD", secondary_y=False)
        fig3.update_yaxes(title_text=" ", secondary_y=True)
        fig3.update_xaxes(rangeslider_visible=True)

        # PROFITABILITY
        ROE = df_FS['Consolidated Income'] / df_FS['Total shareholders equity']
        ROE = ROE.round(3)
        ROA = df_FS['Consolidated Income'] / df_FS['Total assets']
        ROA = ROA.round(3)

        fig4 = make_subplots(specs=[[{"secondary_y": True}]])

        fig4.add_trace(go.Bar(x=Date, y=ROE,
                              opacity=0.25,
                              name='ROE'), secondary_y=True)
        fig4.add_trace(go.Bar(x=Date, y=ROA,
                              opacity=0.25,
                              name='ROA'), secondary_y=True)
        fig4.add_trace(go.Scatter(x=Date, y=df_FS['EBITDA'],
                                  mode='lines+markers',
                                  name='EBITDA'), secondary_y=False)

        fig4.update_layout(title="PROFITABILITY",
                           barmode='group', hovermode='x',legend_orientation="h",legend=dict(x=0, y=-0.65))
        fig4.update_yaxes(title_text="in USD", secondary_y=False)
        fig4.update_yaxes(title_text=" ", secondary_y=True)
        fig4.update_xaxes(rangeslider_visible=True)

        # SOLVENCY & LIQUIDITY
        currentratio = df_FS['Total current assets'] / df_FS['Total current liabilities']
        currentratio = currentratio.round(3)

        response = urlopen("https://financialmodelingprep.com/api/v3/financial-ratios/" + ticker)
        data = response.read().decode("utf-8")
        data_json = json.loads(data)['ratios']

        data_formatted = {}
        for data in data_json:
            date = data['date'][:4]
            del data['date']
            ratio_data = {}

            for key in data.keys():
                ratio_data.update(data[key])

            data_formatted[date] = ratio_data

        data_formatted = pd.DataFrame.from_dict(data_formatted)
        df_fr = data_formatted.T
        df_fr = df_fr.iloc[::-1]
        cols = df_fr.columns
        df_fr[cols] = df_fr[cols].apply(pd.to_numeric, errors='coerce')
        ccc = df_fr['cashConversionCycle'].round(3)

        fig5 = make_subplots(specs=[[{"secondary_y": True}]])
        fig5.add_trace(go.Bar(x=Date, y=df_FS['Debt to Equity'],
                              name='Debt to Equity'), secondary_y=False, )
        fig5.add_trace(go.Bar(x=Date, y=currentratio,
                              name='Current Ratio'), secondary_y=False, )
        fig5.add_trace(go.Scatter(x=Date, y=ccc,
                                  mode='lines+markers',
                                  name='CashConversionCycle'), secondary_y=True, )
        fig5.update_layout(title="SOLVENCY & LIQUIDITY",
                           barmode='group', hovermode='x',legend_orientation="h",legend=dict(x=0, y=-0.7))
        fig5.update_yaxes(title_text=" ", secondary_y=False)
        fig5.update_yaxes(title_text="days", secondary_y=True)
        fig5.update_xaxes(rangeslider_visible=True)

        response = urlopen("https://financialmodelingprep.com/api/v3/quote/" + ticker)
        data = response.read().decode("utf-8")
        quotes = pd.read_json(data).T
        PEratio = quotes.loc["pe"].astype(float).round(2)
        price = quotes.loc["price"]
        eps = quotes.loc["eps"].astype(float).round(2)
        yearrange = quotes.loc["yearLow"].astype(str) + " - " + quotes.loc["yearHigh"].astype(str)

        return fig, fig2, fig3, fig4, fig5, price, PEratio, eps, yearrange

if __name__ == '__main__':
    app.run_server(debug=True)