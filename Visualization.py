import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px


st.set_page_config(page_title="Road Safety Statistics", page_icon=":chart_with_upwards_trend:", layout="wide", initial_sidebar_state="expanded")

time_series_st = st.sidebar.checkbox("Time Series")
time_series_select = None
bar_select = None
if time_series_st :
   time_series_select = st.sidebar.selectbox("Time series Variable", ['Accident junction probability' ,'Casualty count', 'Accidents probability per day of week' ,'Severity probability'], )

bar_st = st.sidebar.checkbox("Bar")

if bar_st :
    bar_select = st.sidebar.selectbox("Bar variable", ["Accidents by hour", "Accidents by road type"])

heatmap_st = st.sidebar.checkbox("Severity heatmap")
# ---------------------------------------------------------------- logic for python -------------------------------------

data = pd.read_csv('./altered_accident_data.csv', low_memory= False)

#---------------------------------------------------------------- line series --------------------------------
if time_series_select is not None:
    if time_series_select == "Accident junction probability":
        sampled_data = data[data.junction_control != 'Data missing or out of range']
        sampled_data.loc[:, 'accident_year'] = pd.to_datetime(sampled_data['accident_year'], format='%Y')
        counts = sampled_data.groupby(['accident_year', 'junction_control']).size().unstack().fillna(0)
        ratios_per_year = counts.div(counts.sum(axis = 1), axis = 0)
        fig = px.line(
            ratios_per_year,
            x=ratios_per_year.index,
            y=ratios_per_year.columns,
            title='Traffic Junction Accident Ratios per Year',
            labels={'x': 'Year', 'y': 'Ratio'},
            line_dash='junction_control',  # Separate lines by traffic junction control
            template='plotly',  # Optional: specify a Plotly template
        )
        st.plotly_chart(fig, use_container_width=True)
    if time_series_select == "Casualty count":
        sampled_data = data.copy()  # Modify this line as needed
        sampled_data['accident_year'] = pd.to_datetime(sampled_data['accident_year'], format='%Y')
        casualty_sums_per_year = sampled_data.groupby('accident_year')['number_of_casualties'].sum().reset_index()

        # Create a line chart using Plotly Express
        fig = px.line(
            casualty_sums_per_year,
            x='accident_year',
            y='number_of_casualties',
            title='Total Casualties by Year',
            labels={'accident_year': 'Year', 'number_of_casualties': 'Total Casualties'},
            template='plotly',  # Optional: specify a Plotly template
        )
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    if time_series_select == 'Accidents probability per day of week':
        # Sample processing
        sampled_data = data.copy()  # Modify this line as needed
        sampled_data['accident_year'] = pd.to_datetime(sampled_data['accident_year'], format='%Y')

        # Calculate the ratio of accidents per day of the week in each year
        daily_ratios = sampled_data.groupby(['accident_year', 'day_of_week']).size().unstack()
        ratios_per_year = daily_ratios.div(daily_ratios.sum(axis=1), axis=0)
        # Create a multi-line time series plot using Plotly Express
        fig = px.line(
            ratios_per_year,
            x=ratios_per_year.index,
            y=ratios_per_year.columns,
            title='Ratio of Accidents by Day of the Week',
            labels={'x': 'Year', 'y': 'Ratio'},
            line_dash='day_of_week',  # Separate lines by day of the week
            template='plotly',  # Optional: specify a Plotly template
        )
        st.plotly_chart(fig, use_container_width=True)
    if time_series_select == 'Severity probability':
        # Sample processing
        sampled_data = data.copy()  # Modify this line as needed
        sampled_data['accident_year'] = pd.to_datetime(sampled_data['accident_year'], format='%Y')
         # Calculate the ratio of severity categories per year
        severity_ratios = sampled_data.groupby(['accident_year', 'accident_severity']).size().unstack()
        ratios_per_year = severity_ratios.div(severity_ratios.sum(axis=1), axis=0)
        # Create a multi-line time series plot using Plotly Express
        fig = px.line(
            ratios_per_year,
            x=ratios_per_year.index,
            y=ratios_per_year.columns,
            title='Ratio of Accidents by Severity',
            labels={'x': 'Year', 'y': 'Ratio'},
            line_dash='accident_severity',  # Separate lines by severity category
            template='plotly',  # Optional: specify a Plotly template
            )
        st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------------- heatmap ----------------------------------------------------------------

if heatmap_st:
    uk_geojson = gpd.read_file('./topo_eer.json')

    severity_counts = data.groupby(['accident_year', 'region_name', 'accident_severity']).size().reset_index(name='count')

    total_counts = data.groupby(['accident_year', 'region_name']).size().reset_index(name='total_count')

    # Merge severity counts with total counts
    merged = severity_counts.merge(total_counts, on=['accident_year', 'region_name'])

    # Calculate severity ratio for each severity level
    merged['severity_ratio'] = merged['count'] / merged['total_count']

    # Pivot the merged DataFrame to get the desired format
    result = merged.pivot(index=['accident_year', 'region_name'], columns='accident_severity', values='severity_ratio').reset_index()

    result['Total Ratio'] = result['Fatal'] + result['Serious']

    merged_data = uk_geojson.merge(result, how='left', left_on='EER13NM', right_on='region_name')

    # Create a choropleth map using Plotly Express
    fig = px.choropleth(
        merged_data,
        geojson=merged_data.geometry,
        locations=merged_data.index,
        color='Total Ratio',
        color_continuous_midpoint=0.14,
        color_continuous_scale='Plasma',
        labels={'Total Ratio': 'Severity'},
        hover_name='EER13NM',
        animation_frame='accident_year')
    fig.update_layout(
        autosize=False,
        width=1200,  # Set the desired width
        height=600  # Set the desired height
    )
    fig.update_geos(fitbounds='locations',visible=False, showland=False, projection_type = "mercator",projection_scale=10)

    st.subheader("Severity Ratio Heatmap")
    st.plotly_chart(fig, use_container_width=True)
#---------------------------------------------------------------- bar charts --------------------------------

if bar_select is not None:
    if bar_select == 'Accidents by hour':
        data['time'] = pd.to_datetime(data['time'], format='%H:%M').dt.time
        data['hour'] = data['time'].apply(lambda x: x.hour)
        grouped_counts = data.groupby('hour')['accident_reference'].count().reset_index(name='count')
        fig = px.bar(grouped_counts, x='hour', y='count', color='hour',
             labels={'hour': 'Hour of the Day', 'count': 'Number of Accidents'},
             title='Total Accident Counts by Hour and Reference')
        st.plotly_chart(fig, use_container_width=True)

    if bar_select == 'Accidents by road type':
        data = data.dropna(subset=['road_type'])
        road_type_counts = data.groupby('road_type')['accident_reference'].count().reset_index()
        # Create a bar chart using Plotly
        fig = px.bar(road_type_counts, x='road_type', y='accident_reference', labels={'road_type': 'Road Type', 'accident_reference': 'Number of Accidents'},
                    title='Accident Counts by Road Type')
        # Display the Plotly chart using st.plotly_chart()
        st.plotly_chart(fig, use_container_width=True)
