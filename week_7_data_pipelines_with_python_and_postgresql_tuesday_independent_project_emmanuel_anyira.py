# -*- coding: utf-8 -*-
"""Week 7 Data Pipelines with Python and PostgreSQL Tuesday Independent Project- Emmanuel Anyira.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15n_kJlofTMWPNIoUGEWTp5Ha4E7z0fJu

**Project Deliverable**

A GitHub repository with a python file (.py) with your solution.

**Problem Statement**
Equipment failure is a major cause of downtime in the telecommunications industry, which can result in significant financial losses and customer dissatisfaction. To minimize downtime and ensure optimal performance, it is crucial to identify potential equipment failures and schedule
maintenance accordingly proactively. This requires the collection and analysis of large amounts of data generated by various equipment and network sensors.
The deliverable for this project is a data pipeline that can efficiently collect, clean, and analyze equipment and network sensor data. The pipeline should be designed to identify potential equipment failures and schedule maintenance proactively, minimizing downtime and improving overall equipment performance. The data pipeline will be built using Python and PostgreSQL
and with the Postgres database hosted on Google Cloud.
Guidelines.

Here are some guidelines and hints to help you create the data pipeline:

● Data Extraction: The data pipeline should be designed to collect data from various sources, including network sensors, equipment sensors, and maintenance records.
Sample datasets for data extraction will be provided by the client and should be used for building the pipeline.

● Data Transformation: The collected data must be cleaned and transformed to ensure consistency and quality. This will involve removing duplicates, fixing missing data, and normalizing the data for consistency. You can also explore the following techniques:
○ Aggregation: Summarizing data into useful metrics such as the total number of
equipment failures, average time between failures, etc.
○ Joining: Combining multiple datasets based on common fields or keys to create a
unified view of the data.
○ Data enrichment: Combining internal data with external data sources such as
weather data or other publicly available datasets to gain additional insights.

● Data Analysis: The cleaned data will be used to build machine learning models that can predict potential equipment failures and schedule maintenance proactively. The models will be designed to analyze equipment and network sensor data in real time to identify anomalies and predict potential failures. You don’t need to implement this step in the data pipeline.

● Data Loading: The resulting data will be stored in a PostgreSQL database.
Sample Datasets for Data Extraction
Sample datasets (https://bit.ly/3YNdO2Y) will be provided by the client for data extraction. 
The
datasets will include equipment sensor data, network sensor data, and maintenance records.

The datasets will be in CSV format and will include the following fields:

1.   Equipment sensor data: ID, date, time, sensor reading
2.   Network sensor data: ID, date, time, sensor reading
3.   Maintenance records: ID, date, time, equipment ID, maintenance type

Installing Psycopg2
"""

!pip install psycopg2-binary

"""Importing the necessary libraries"""

import pandas as pd
from sqlalchemy import create_engine

"""Defining the database connection"""

# Defining the Google Cloud PostgreSQL database connection to be used by the pipeline
POSTGRES_ADDRESS = '35.237.226.12'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'postgres'
POSTGRES_PASSWORD = 'password'
POSTGRES_DBNAME = 'telecommunications_data'

"""Defining the database engine and apssing the set variables"""

# Defining the database engine to be used to insert data
postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
                .format(username=POSTGRES_USERNAME,
                        password=POSTGRES_PASSWORD,
                        ipaddress=POSTGRES_ADDRESS,
                        port=POSTGRES_PORT,
                        dbname=POSTGRES_DBNAME))
engine = create_engine(postgres_str)

"""Data extraction: The data pipeline should be designed to collect data from various sources, including network sensors, equipment sensors, and maintenance records.
Sample datasets for data extraction will be provided by the client and should be used for building the pipeline.

"""

def extract_sensor_data():
    # Loading the equipment sensor data into a DataFrame
    equipment_sensor_df = pd.read_csv('equipment_sensor.csv')

    # Load the network sensor data into a DataFrame
    network_sensor_df = pd.read_csv('network_sensor.csv')

    # Load the maintenance records data into a DataFrame
    maintenance_sensor_df = pd.read_csv('maintenance_records.csv')

    return equipment_sensor_df, network_sensor_df, maintenance_sensor_df

"""Data Transformation: The collected data must be cleaned and transformed to ensure consistency and quality. This will involve removing duplicates, fixing missing data, and normalizing the data for consistency. You can also explore the following techniques:
 
1.   Aggregation: Summarizing data into useful metrics such as the total number of equipment failures, average time between failures, etc.

2.   Joining: Combining multiple datasets based on common fields or keys to create a unified view of the data

3. Data enrichment: Combining internal data with external data sources such as
weather data or other publicly available datasets to gain additional insights.


"""

def transform_sensor_data(equipment_sensor_df, network_sensor_df, maintenance_sensor_df):
    # Removing duplicates for easy analysis
    equipment_sensor_df.drop_duplicates(inplace=True)
    network_sensor_df.drop_duplicates(inplace=True)
    maintenance_sensor_df.drop_duplicates(inplace=True)

    # Fixing missing data for easy analysis
    equipment_sensor_df.fillna(method='ffill', inplace=True)
    network_sensor_df.fillna(method='ffill', inplace=True)
    maintenance_sensor_df.fillna(method='ffill', inplace=True)

    # Normalizing the data for consistency and easy analysis
    equipment_sensor_df['date_time'] = pd.to_datetime(equipment_sensor_df['date'] + ' ' + equipment_sensor_df['time'])
    equipment_sensor_df.drop(['date', 'time'], axis=1, inplace=True)

    network_sensor_df['date_time'] = pd.to_datetime(network_sensor_df['date'] + ' ' + network_sensor_df['time'])
    network_sensor_df.drop(['date', 'time'], axis=1, inplace=True)

    maintenance_sensor_df['date_time'] = pd.to_datetime(maintenance_sensor_df['date'] + ' ' + maintenance_sensor_df['time'])
    maintenance_sensor_df.drop(['date', 'time'], axis=1, inplace=True)

    # Aggregating the data
    equipment_summary = equipment_sensor_df.groupby('ID').agg({'date_time': ['min', 'max'], 'sensor_reading': ['mean', 'max']})
    equipment_summary.columns = ['first_seen', 'last_seen', 'average_reading', 'max_reading']
    network_summary = network_sensor_df.groupby('ID').agg({'date_time': ['min', 'max'], 'sensor_reading': ['mean', 'max']})
    network_summary.columns = ['first_seen', 'last_seen', 'average_reading', 'max_reading']

    # Joining the data from the equipment and network sensor data sets
    sensor_summary = pd.merge(equipment_summary, network_summary, how='outer', left_index=True, right_index=True)
    sensor_summary = sensor_summary.reset_index()
    sensor_summary = sensor_summary.rename(columns={'ID': 'equipment_ID'})

    maintenance_df = maintenance_sensor_df[['date_time', 'equipment_ID', 'maintenance_type']]

    return sensor_summary, maintenance_df

"""Data Loading: The resulting data will be stored in a PostgreSQL database."""

def load_sensor_data(sensor_summary, maintenance_df):
    # Loading the data to PostgreSQL using to_sql function
    sensor_summary.to_sql('sensor_summary', engine, if_exists='replace')
    maintenance_df.to_sql('maintenance_records', engine, if_exists='replace')

"""Defining the main function.

extract_sensor_data() is called to read data from three sources: equipment_sensor_df, network_sensor_df, and maintenance_sensor_df.

transform_sensor_data() is called to process and merge the three data sources into two dataframes: sensor_summary and maintenance_sensor_df.

load_sensor_data() is called to load the two dataframes into their respective tables.

It's common for main() to be the entry point of a Python program. The program starts executing from this function. The functions extract_sensor_data(), transform_sensor_data(), and load_sensor_data() are usually defined elsewhere in the program.

To execute this program, you would call main() from within another Python script or from the command line.
"""

def main():
    equipment_sensor_df, network_sensor_df, maintenance_sensor_df = extract_sensor_data()
    sensor_summary, maintenance_df = transform_sensor_data(equipment_sensor_df, network_sensor_df, maintenance_sensor_df)
    load_sensor_data(sensor_summary, maintenance_df)
    
if __name__ == '__main__':
    main()