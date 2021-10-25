import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

pd.options.mode.chained_assignment = None


res = requests.get('https://data.tradeui.com/tui_sweeps?idT=aa')

res = res.json() # convert to json
res = np.array(res)

df = pd.DataFrame.from_dict(pd.json_normalize(res), orient='columns')

df = df[['time','put_call','aggressor_ind','option_activity_type','strike_price','option_symbol','date_expiration','cost_basis']]

df.rename(columns={'time':'Time','put_call':'C/P','aggressor_ind':'Side','option_activity_type':'Type','strike_price':'Strike','option_symbol':'Stock','date_expiration':'Expiration','cost_basis':'Prems'},inplace=True)


#Side is aggressor_ind if 0.5 its Mid, if negative its below bid if less than 0.5 its bid. If over 0.5 it's ask if 1 or above above ask
for i in df.index.values:
    if (df['Side'][i] >=0) & (df['Side'][i] <= 0.5):
        df['Side'][i] = 'B'
    elif df['Side'][i] < 0:
        df['Side'][i] = 'BB'
    elif (df['Side'][i] > 0.5) & (df['Side'][i] < 1):
        df['Side'][i] = 'A'
    elif df['Side'][i] >= 1:
        df['Side'][i] = 'AA'


df['Expiration'] = df['Expiration'].str.slice(stop=10)
df['Expiration'] = pd.to_datetime(df.Expiration)

df['Expiration'] = df['Expiration'].dt.strftime('%m/%d/%Y')


fig = go.Figure()

map_color_cp = {"PUT":"rgb(247,69,101)","CALL":"rgb(7,186,111)"}

map_color_side = {"AA":"rgb(14,132,206)","BB":"rgb(175,82,201)","A":"rgb(29,42,55)","B":"rgb(29,42,55)"}

map_color_type = {"SWEEP":"rgb(211,143,8)","TRADE":"rgb(29,42,55)"}



df["color_cp"] = df["C/P"].map(map_color_cp)

df["color_side"] = df["Side"].map(map_color_side)

for i in df.index.values:
    n = i%2
    if (df['Side'][i] != "AA") & (df['Side'][i] != "BB"):
        if n == 0:
            df['color_side'][i] = "rgb(20,29,38)"


df['color_type'] = df['Type'].map(map_color_type)

for i in df.index.values:
    n = i%2
    if (df['Type'][i] != "SWEEP"):
        if n == 0:
            df['color_type'][i] = "rgb(20,29,38)"

cols_to_show = ["Time","C/P", "Side", "Type","Strike","Stock","Expiration","Prems"]

fill_color = []
line_color = []
n = len(df)
for col in cols_to_show:
    if col == 'C/P':
        fill_color.append(df["color_cp"].to_list())
        line_color.append(df["color_cp"].to_list())
    elif col == 'Side':
        fill_color.append(df["color_side"].to_list())
        line_color.append(df["color_side"].to_list())
    elif col == 'Type':
        fill_color.append(df["color_type"].to_list())
        line_color.append(df["color_type"].to_list())
    else:
        fill_color.append(np.resize(['#141d26','#1d2a37'], n))
        line_color.append(np.resize(['#141d26','#1d2a37'], n))


fig.add_trace(
    go.Table(
        header=dict(
            values=[f"<b>{col}</b>" for col in cols_to_show],
            align="center",
            line_color='#141d26', fill_color='#141d26',
            font=dict(color='white', size=24)
        ),
        cells=dict(
            values=df[cols_to_show].values.T,
            line_color=line_color, fill_color=fill_color,
            font = dict(color = 'white', size = 20),
            align = "center",
            height= 30
        )
    )
)

fig.layout.images = [dict(
        source="https://i.ibb.co/y6PVjyn/logo.png",
        xref="paper", yref="paper",
        x=-0.03, y=-0.09,
        sizex=0.1, sizey=0.1,
        xanchor="center", yanchor="bottom"
      )]

layout = go.Layout(
    title_text="SPY Biggest Flow",
    title_x=0.5,
    paper_bgcolor='#141d26',
    plot_bgcolor='#141d26',
    font_family='Monospace',
    font_color='white',
    font_size=32,
    margin=dict(
        l=100,
        r=100,
    ),
     annotations=[
        go.layout.Annotation(
            showarrow=False,
            text='15 minutes delayed flow data. Please visit www.tradytics.com to get access to realtime data.',
            xanchor='center',
            x=0.5,
            yanchor='middle',
            y=-0.07,
            font=dict(size=15,color='#72777c')
        )]
)

fig.update_layout(layout)

fig.show()

fig.write_html("table.html")
