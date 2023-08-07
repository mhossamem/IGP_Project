import streamlit as st
import pickle
import numpy as np

from sklearn.svm import LinearSVC
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier 
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import xgboost as xgb
from sklearn.metrics import classification_report


# Streamlit UI
st.title('Accident Severity Prediction Application')

st.sidebar.header('Input Features')

list_of_models_file_names = ['gradient_cost_sensitive', 'logistic_default', 'naive_default', 'random_default', 'support_over']

list_of_models = ['All','Gradient Cost Sensitive', 'Logistic Regression', 'Naive Bayes Regression', 'Random Forest', 'SVM']

loaded_model = st.selectbox('Choose Classification Model', list_of_models)

uploaded_model = st.file_uploader('or Upload your own model (Max 200MB)', type=['pkl'],accept_multiple_files=False)

# Load the trained model
def get_model():
    models = []
    if list_of_models.index(loaded_model) == 0:
        for i in range(len(list_of_models_file_names)):
            models.append(load_model(list_of_models_file_names[i]))
    else:
        models = load_model(list_of_models_file_names[list_of_models.index(loaded_model) - 1])
    return models

                            

def load_model(model_name):
    with open('./models/{}.pkl'.format(model_name), 'rb') as model_file:
        model = pickle.load(model_file)
    return model
# Input fields
number_of_vehicles = st.sidebar.number_input('Number of Vehicles', min_value=1, value=1)
number_of_casualties = st.sidebar.number_input('Number of Casualties', min_value=0, value=0)
day_of_week = st.sidebar.selectbox('Day of Week', ['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
time = st.sidebar.slider('Time', 0, 23, 12)
first_road_class = st.sidebar.selectbox('First Road Class', ['Motorway', 'Other'])
road_type = st.sidebar.selectbox('Road Type', ['Single Carriageway', 'Other'])
speed_limit = st.sidebar.selectbox('Speed Limit', [20, 30, 40, 50, 60, 70])
junction_detail = st.sidebar.checkbox('Junction Detail')
pedestrian_crossing_human_control = st.sidebar.checkbox('Pedestrian Crossing Human Control')
pedestrian_crossing_physical_facilities = st.sidebar.checkbox('Pedestrian Crossing Physical Facilities')
light_conditions = st.sidebar.checkbox('Daytime')
weather_conditions = st.sidebar.checkbox('Fine Weather Conditions')
road_surface_conditions = st.sidebar.checkbox('Good Road Surface Conditions')
special_conditions_at_site = st.sidebar.checkbox('Special Conditions at Site')
carriageway_hazards = st.sidebar.checkbox('Carriageway Hazards')
urban_or_rural_area = st.sidebar.selectbox('Urban or Rural Area', ['Urban', 'Rural'])
_2_or_3_wheel = st.sidebar.checkbox('Bicycle or Motorcycle involved')
General_Cars = st.sidebar.checkbox('General Cars')
Other_vehicles = st.sidebar.checkbox('Other Vehicles (SUV, Jeep, Truck)')
Under_25 = st.sidebar.checkbox('Drivers Under 25')
Over_65 = st.sidebar.checkbox('Drivers Over 65')
Others = st.sidebar.checkbox('Other age group')
predict_button = st.sidebar.button("Predict")

day_of_week_dict = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, 'Friday': 6, 'Saturday': 7}
# Transforming inputs
day_of_week_encoded = day_of_week_dict[day_of_week]
time_category = 0 if 7 <= time <= 20 else 1
first_road_class_encoded = 0 if first_road_class == 'Motorway' else 1
road_type_encoded = 0 if road_type == 'Single Carriageway' else 1
junction_detail_encoded = 1 if junction_detail else 0
pedestrian_crossing_human_control_encoded = 1 if pedestrian_crossing_human_control else 0
pedestrian_crossing_physical_facilities_encoded = 1 if pedestrian_crossing_physical_facilities else 0
light_conditions_encoded = 1 if light_conditions else 0
weather_conditions_encoded = 1 if weather_conditions else 0
road_surface_conditions_encoded = 1 if road_surface_conditions else 0
special_conditions_at_site_encoded = 1 if special_conditions_at_site else 0
carriageway_hazards_encoded = 1 if carriageway_hazards else 0
urban_or_rural_area_encoded = 0 if urban_or_rural_area == 'Urban' else 1
_2_or_3_wheel_encoded = 1 if _2_or_3_wheel else 0
General_Cars_encoded = 1 if General_Cars else 0
Other_vehicles_encoded = 1 if Other_vehicles else 0
Under_25_encoded = 1 if Under_25 else 0
Over_65_encoded = 1 if Over_65 else 0
Others_encoded = 1 if Others else 0


# Make prediction
features = np.array(
    [number_of_vehicles, number_of_casualties, day_of_week_encoded, time_category, first_road_class_encoded,
    road_type_encoded, speed_limit, junction_detail_encoded, pedestrian_crossing_human_control_encoded,
    pedestrian_crossing_physical_facilities_encoded, light_conditions_encoded, weather_conditions_encoded,
    road_surface_conditions_encoded, special_conditions_at_site_encoded, carriageway_hazards_encoded,
    urban_or_rural_area_encoded, _2_or_3_wheel_encoded, General_Cars_encoded, Other_vehicles_encoded, Under_25_encoded, Over_65_encoded, Others_encoded
])

if predict_button: 
    if uploaded_model is None:
        model = get_model()
    else:
                model = pickle.load(uploaded_model)
    features.reshape(1,-1)
    print([features])
    print(model)
    if(isinstance(model, list)):
        for index,md in model:
            if index != 0:
                prediction = md.predict([features])
                severity = {0:'Severe/Fatal', 1:'Slight'}
                st.write("Predicted Accident Severity for {} is {}".format(list_of_models[index + 1],severity[prediction[0]]))

    else:
        prediction = model.predict([features])
        severity = {0:'Severe/Fatal', 1:'Slight'}
        st.write("Predicted Accident Severity is {}".format(severity[prediction[0]]))
