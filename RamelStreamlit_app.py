
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

df = pd.read_csv("https://raw.githubusercontent.com/Parhelion2222/ICSramelstreamlit/main/Data_Sample/alcohol_use.csv")
df_states = pd.read_csv("https://raw.githubusercontent.com/jasonong/List-of-US-States/master/states.csv")

st.title('US Alcohol Consumption Between 1977 and 2023')
st.markdown('Use the filters below to explore alcohol consumption across US states from 1977 to 2023.')

#Merging two data sets
df_states['State'] = df_states['State'].str.lower()
df = df.merge(df_states, left_on="state", right_on="State", how="left")

#Grouping each state to the region they belong to
region_lookup = {
    'CT':'Northeast','ME':'Northeast','MA':'Northeast','NH':'Northeast',
    'RI':'Northeast','VT':'Northeast','NY':'Northeast','NJ':'Northeast','PA':'Northeast',
    'IL':'Midwest','IN':'Midwest','MI':'Midwest','OH':'Midwest','WI':'Midwest',
    'IA':'Midwest','KS':'Midwest','MN':'Midwest','MO':'Midwest','NE':'Midwest',
    'ND':'Midwest','SD':'Midwest',
    'DE':'South','FL':'South','GA':'South','MD':'South','NC':'South',
    'SC':'South','VA':'South','WV':'South','AL':'South','KY':'South',
    'MS':'South','TN':'South','AR':'South','LA':'South','OK':'South','TX':'South',
    'DC':'South',
    'AZ':'West','CO':'West','ID':'West','MT':'West','NV':'West','NM':'West',
    'UT':'West','WY':'West','AK':'West','CA':'West','HI':'West','OR':'West','WA':'West'
}

df['region'] = df['Abbreviation'].map(region_lookup)

#Filtering Region Data from alcohol_use.csv
region_data = ['Midwest Region','Northeast Region','South Region','West Region','Us Total']
df = df[~df['state_name'].isin(region_data)].copy()

#Informationsper state
df['text'] = df['state_name'] + '<br>' + \
    'Beer: ' + df['ethanol_beer_gallons_per_capita'].astype(str) +  '<br>' + \
    ' Wine: ' + df['ethanol_wine_gallons_per_capita'].astype(str) + '<br>' + \
    'Spirit: ' + df['ethanol_spirit_gallons_per_capita'].astype(str) + '<br>' + \
    'Total: ' + df['ethanol_all_drinks_gallons_per_capita'].astype(str)

#Filtering years from oldest to newest
df_1977 = df[df['year'] == 1977].copy()
df_2023 = df[df['year'] == 2023].copy()

#This is to keep the values of the two different years the same as the other 
zmin = min(df_1977['ethanol_all_drinks_gallons_per_capita'].min(),
           df_2023['ethanol_all_drinks_gallons_per_capita'].min())

zmax = max(df_1977['ethanol_all_drinks_gallons_per_capita'].max(),
           df_2023['ethanol_all_drinks_gallons_per_capita'].max())

#Displaying map comparison between two different years
def map_comparison(data, year, region):
    fig = go.Figure(data=go.Choropleth(
        locations=data['Abbreviation'],
        z=data['ethanol_all_drinks_gallons_per_capita'].astype(float),
        locationmode='USA-states',
        colorscale='Reds',
        autocolorscale=False,
        zmin=zmin,                                     
        zmax=zmax,  
        text=data['text'],
        marker_line_color='white',
        colorbar=dict(
            title=dict(text="Gallons per Capita"),
            thickness=15,
            len=0.5,
            x=1.0,
            y=0.5
        )
    ))
    fig.update_layout(
        title_text=f'{year} US Alcohol Consumption — {region}',
        margin=dict(l=30, r=30, t=30, b=30),
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255,255,255)',
        )
    )
    return fig

#User choosing which region to visualize 
selected_region = st.selectbox(
    'Filter by Region',
    options=['All USA', 'Northeast', 'Midwest', 'South', 'West']
)

#User choosing which states to visualize
selected_states = st.multiselect(
    'Filter by State (leave empty to show all)',
    options=sorted(df['state_name'].dropna().unique().tolist())
)

#Vizualizes all states
if selected_region != 'All USA':
    df_1977 = df_1977[df_1977['region'] == selected_region].copy()
    df_2023 = df_2023[df_2023['region'] == selected_region].copy()

#Filters by selected states if any are chosen
if selected_states:
    df_1977 = df_1977[df_1977['state_name'].isin(selected_states)].copy()
    df_2023 = df_2023[df_2023['state_name'].isin(selected_states)].copy()

#Edge case handling when filters result in empty data
if df_1977.empty or df_2023.empty:
    st.warning('No data available for the selected filters. Please adjust your selection.')
    st.stop()

#Displaying two visualization with one another
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        map_comparison(df_1977, 1977, selected_region),
        width='stretch'
    )

with col2:
    st.plotly_chart(
        map_comparison(df_2023, 2023, selected_region),
        width='stretch'
    )

st.subheader('Regional Alcohol Consumption Trends Over Time')

#User choosing which year range to visualize
year_range = st.slider(
    'Select Year Range',
    min_value=1977,
    max_value=2023,
    value=(1977, 2023)
)

#Grouping yearly data in each region to calculate the sum of ethanol_all_drinks_gallons_per_capita
df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])].copy()

#Summary statistics that update based on year range filter
st.subheader('Summary Statistics')
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric('Avg Total', f"{df_filtered['ethanol_all_drinks_gallons_per_capita'].mean():.2f} gal")
with col_b:
    st.metric('Avg Beer', f"{df_filtered['ethanol_beer_gallons_per_capita'].mean():.2f} gal")
with col_c:
    st.metric('Avg Wine', f"{df_filtered['ethanol_wine_gallons_per_capita'].mean():.2f} gal")
with col_d:
    st.metric('Avg Spirit', f"{df_filtered['ethanol_spirit_gallons_per_capita'].mean():.2f} gal")

yearly_total = df_filtered.groupby('year')['ethanol_all_drinks_gallons_per_capita'].mean().reset_index()

#Group by year and region for all 4 regions
region_yearly = df_filtered.groupby(['year', 'region'])['ethanol_all_drinks_gallons_per_capita'].mean().reset_index()

northeast = region_yearly[region_yearly['region'] == 'Northeast']
midwest   = region_yearly[region_yearly['region'] == 'Midwest']
south     = region_yearly[region_yearly['region'] == 'South']
west      = region_yearly[region_yearly['region'] == 'West']

fig = go.Figure()

#Adding each region a visualization for stacked line chart
fig.add_trace(go.Scatter(
    x=northeast['year'], y=northeast['ethanol_all_drinks_gallons_per_capita'],
    name='Northeast', mode='lines+markers',
    line=dict(color='Red', width=1.5), marker=dict(size=5)
))

fig.add_trace(go.Scatter(
    x=midwest['year'], y=midwest['ethanol_all_drinks_gallons_per_capita'],
    name='Midwest', mode='lines+markers',
    line=dict(color='Blue', width=1.5), marker=dict(size=5)
))

fig.add_trace(go.Scatter(
    x=south['year'], y=south['ethanol_all_drinks_gallons_per_capita'],
    name='South', mode='lines+markers',
    line=dict(color='Green', width=1.5), marker=dict(size=5)
))

fig.add_trace(go.Scatter(
    x=west['year'], y=west['ethanol_all_drinks_gallons_per_capita'],
    name='West', mode='lines+markers',
    line=dict(color='Yellow', width=1.5), marker=dict(size=5)
))

fig.update_layout(
    title=f'Total Alcohol Consumption by Region ({year_range[0]}–{year_range[1]})',
    hovermode='x unified',
    height=500,
    template='plotly_white',
    xaxis=dict(title='Year'),
    yaxis=dict(title='Gallons per Capita'),
    margin=dict(t=60, b=60)
)

st.plotly_chart(fig, width='stretch')

st.subheader('Beer vs Wine vs Spirit Total Consumption Comparison')

#User choosing which year to compare
selected_years = st.radio(
    '',
    options=['1977 only', '2023 only', 'Both'],
    horizontal=True
)

fig = go.Figure()

#Conditional Statements Based on the Button pressed by the user
if selected_years in ['1977 only', 'Both']:
    fig.add_trace(go.Bar(
        name='1977',
        x=['Beer', 'Wine', 'Spirit'],
        y=[
            df_1977['ethanol_beer_gallons_per_capita'].sum(),
            df_1977['ethanol_wine_gallons_per_capita'].sum(),
            df_1977['ethanol_spirit_gallons_per_capita'].sum()
        ],
        error_y=dict(
            type='data',
            array=[
                df_1977['ethanol_beer_gallons_per_capita'].std(),
                df_1977['ethanol_wine_gallons_per_capita'].std(),
                df_1977['ethanol_spirit_gallons_per_capita'].std()
            ]
        ),
        marker_color='Orange'
    ))

if selected_years in ['2023 only', 'Both']:
    fig.add_trace(go.Bar(
        name='2023',
        x=['Beer', 'Wine', 'Spirit'],
        y=[
            df_2023['ethanol_beer_gallons_per_capita'].sum(),
            df_2023['ethanol_wine_gallons_per_capita'].sum(),
            df_2023['ethanol_spirit_gallons_per_capita'].sum()
        ],
        error_y=dict(
            type='data',
            array=[
                df_2023['ethanol_beer_gallons_per_capita'].std(),
                df_2023['ethanol_wine_gallons_per_capita'].std(),
                df_2023['ethanol_spirit_gallons_per_capita'].std()
            ]
        ),
        marker_color='SkyBlue'
    ))

fig.update_layout(
    title=f'Alcohol Consumption by Type — {selected_years}',
    barmode='group',
    yaxis=dict(title='Gallons per Capita'),
    height=400,
    template='plotly_white'
)

st.plotly_chart(fig, width='stretch')
