# ski-tracking-sim
MGT-555 | Ski tracking simulation + dashboard

## Overview
Repo containing two pieces of code used to develop our ski tracking algorithm.
1- ETL pipeline to extract data from a .csv files and generate an interpretable file for the visualization dashboard.
2- Visualization dashboard to display the data and the algorithm results.

## ETL pipeline
The ETL pipeline is a jupyter notebook that takes raw sensor data dumped from an Android device and generates a file that can be used by the visualization dashboard.
First, a .csv file is generated from the Android device. This file contains the raw sensor data.
Afterwards, a first low-pass filtering is done by averaging readings over a single second. This is done to remove high-frequency noise from the data and to synchronize readings.
Features are generated and extracted from this first low-pass filtering data. The features are the following:
- Current Altitude
- Change in Altitude over short-time window
- Change in Altitude over long-time window
Finally, a finite state machine with three states (SKIING, LIFT, IDLE) is driven from these features.

When the user is in SKIING state, his metrics are monitored. When the user exits the SKIING state, the cumulative metrics are updated and the current run metrics are reset.

At the end, a .csv file is generated for the Dashboard to consume

## Dashboard
The dashboard is a web application that displays the data and the algorithm results. It is built using Plotly Dash.
It shows the current run info, the cumulative info from the day, the position of the skier on the mountain, his altitude et his current state.
It is used to show the algorithm results in real-time and to visualize the results.