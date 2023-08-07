import pandas as pd 
import numpy as np
import time

start = time.time()
def mapping_func(table_name, names, df):
    labels_sub = labels[labels.table == table_name][['field name', 'code', 'label']]
    for i in names:
        if i in df.columns:
            mapping_dict = labels_sub[labels_sub['field name'] == i].groupby('code')['label'].apply(lambda x: x.iloc[0] if not x.empty else np.nan).to_dict()
            df[i] = df[i].map(mapping_dict)
            

def map_local_authority_to_region_name(xls_f, sheet_name, from_mapped, to_mapped, df):
    regions = pd.read_excel(xls_f, sheet_name=sheet_name)
    
    mapping_dict = regions.set_index(from_mapped)[to_mapped].to_dict()
    
    # Replace column values using the mapping dictionary
    df[to_mapped] = df[to_mapped].map(mapping_dict)



acc = pd.read_csv('dft-road-casualty-statistics-accident-1979-2021.csv', low_memory=False)
acc = acc[acc.accident_year >= 2016]
labels = pd.read_excel('Road-Safety-Open-Dataset-Data-Guide.xlsx')
labels.rename(columns={labels.columns[2]:'code'}, inplace=True) 

# Filter and drop unnecessary columns for 'Accident' data. You can edit this list to keep columns.
acc_drop = ['location_easting_osgr', 'location_northing_osgr','police_force',
           'local_authority_district','local_authority_highway', 'first_road_class', 'first_road_number',
           'second_road_class', 'second_road_number','did_police_officer_attend_scene_of_accident','lsoa_of_accident_location', 'special_conditions_at_site', 'carriageway_hazards',
       'urban_or_rural_area', 'trunk_road_flag','pedestrian_crossing_human_control',
       'pedestrian_crossing_physical_facilities' ]
acc.drop(columns=acc_drop, inplace=True)

# You can also edit this list to transform desired colums if you keeping them and needs to transform.
names_acc = ['accident_severity','day_of_week','local_authority_ons_district', 'road_type', 'speed_limit',
       'junction_detail', 'junction_control','light_conditions',
       'weather_conditions', 'road_surface_conditions',]


mapping_func('Accident', names_acc, acc)

acc.rename(columns = {'local_authority_ons_district': 'region_name'}, inplace= True)

map_local_authority_to_region_name('./laregionlookup376las.xls','LA_region_lookup', 'la_name','region_name',acc)

acc.to_csv("altered_accident_data.csv", index=False)