import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
st.write('<div style="text-align: center;"><span style="font-size: 24px;">Analysis of Electric Power Required for Light-Duty Vehicles in California</span></div>', unsafe_allow_html=True)
st.write('<div style="text-align: center;"><span style="font-size: 24px;">\n</span></div>', unsafe_allow_html=True)

st.write('<p style="font-family: cursive; font-size: 16px; text-align: center;">Developed by <a href="https://www.linkedin.com/in/oshanreh/" style="color: #ff69b4; text-decoration: none;">Mohammad Mehdi Oshanreh</a></p>', unsafe_allow_html=True)
st.write('<span style="font-size: 16px; color: red; font-weight: bold;">Please refer to the blog post for the assumptions made for calculating the power needed.</span>', unsafe_allow_html=True)

# Constants.
st.write('<span style="font-size: 24px;">Select Management Scenario</span>', unsafe_allow_html=True)
st.write('<span style="font-size: 16px;">In the managed scenario, all cars are assumed to be charged from 8 AM to 4 PM, within an 8-hour time  (Ideal Situation). \n In the unmanaged scenario, cars can be plugged into the charger at any time throughout the day.</span>', unsafe_allow_html=True)

sit = st.selectbox("", ["Managed", "Unmanaged"])
time_steps = 8
if sit =='Unmanaged':
    time_steps = 24

st.write('<span style="font-size: 24px;">Choose Number of Cars to be Charged Daily</span>', unsafe_allow_html=True)
st.write('<span style="font-size: 16px;">Lower value assumes that not all cars are used and charged daily. \n Upper value assumes an extreme condition where all cars are being used and charged daily.</span>', unsafe_allow_html=True)

total_cars_option = st.selectbox("", ["23.2 Millon","30.8 Million"])
total_cars=23200000
ex= 'Normal'

if total_cars_option == "30.8 Million":
    total_cars = 30800000
    ex = 'Extreme'


#avg_battery_size = st.number_input('Average Battery Size (KWh)', value=9)
st.write('<span style="font-size: 24px;">Select Average Charger Power</span>', unsafe_allow_html=True)
st.write('<span style="font-size: 16px;">The electric power required to meet BEV charging demand is directly proportional to the power rating of the charger. </span>', unsafe_allow_html=True)
st.write('<span style="font-size: 16px;"We assumed only these two types are used to charge BEVs.</span>', unsafe_allow_html=True)

level_two_power =st.slider('Level Two Power (KW)', 3, 20, step=1, value=10)
dc_power = st.slider('DC Fast Power (KW)', 50, 400, step=50, value=150)

st.write('<span style="font-size: 24px;">Select Average Proportion of vehicles to be Charged by Level 2 Chargers</span>', unsafe_allow_html=True)

level_two_percent = st.slider('Level 2 Charger Proportion', 0.0, 1.0, 0.5)
dc_fast_percent = 1 - level_two_percent

np.random.seed(0)

# Distributions
distributions = ['Poisson', 'Uniform', 'Normal', 'Extreme']
peak_powers = {}

for distribution in distributions:
    if distribution == 'Poisson':
        lam = total_cars / time_steps
        cars_charging = np.random.poisson(lam, time_steps)
    elif distribution == 'Uniform':
        cars_charging = np.full(time_steps, total_cars // time_steps)
    elif distribution == 'Normal':
        mean = total_cars / time_steps
        std_dev = total_cars / 4  # Assumption
        cars_charging = np.abs(np.random.normal(mean, std_dev, size=time_steps)).astype(int)
    elif distribution == 'Extreme':
        cars_charging = np.zeros(time_steps)
        cars_charging[0] = total_cars

    level_two_draw = cars_charging * level_two_power * level_two_percent
    dc_fast_draw = cars_charging * dc_power * dc_fast_percent
    total_power_draw = level_two_draw + dc_fast_draw

    peak_powers[distribution] = [np.max(level_two_draw) / 1e6, np.max(dc_fast_draw) / 1e6]

distribution_labels = peak_powers.keys()
level_two_values = [values[0] for values in peak_powers.values()]
dc_fast_values = [values[1] for values in peak_powers.values()]

bar_width = 0.35
index = np.arange(len(distribution_labels))

fig, ax = plt.subplots()

ax.bar(index, level_two_values, bar_width, label='Level 2')
ax.bar(index, dc_fast_values, bar_width, bottom=level_two_values, label='DC Fast')

ax.set_xticks(index)
ax.set_xticklabels(distribution_labels)
ax.set_xlabel('Charging Behavior')
ax.set_ylabel('Peak Power (GW)')
b = [i + j for i in dc_fast_values for j in level_two_values]
mx = max(b)
lag = ceil((max(b) / 100)) * 10
ax.set_yticks([lag * i for i in range(11)])
ax.set_title('Maximum Power Needed for {} Scenario in {} Condition'.format(sit, ex))
ax.legend(title='Market Share: \nLevel 2: %.0f%%       DC Fast: %.0f%% \n Charger Nominal Power \nLevel 2: %.0f KW    DC Fast: %.0f KW' % (level_two_percent * 100, dc_fast_percent * 100, level_two_power, dc_power), loc='upper left')
st.pyplot(fig)
