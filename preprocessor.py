import re
import pandas as pd
import streamlit as st

def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s|\u00A0|\u202F)?[apAP][mM]\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    for timestamp in dates:
        cleaned = timestamp.replace('\u202f', ' ').replace('\u00A0', ' ')

    df = pd.DataFrame({'user_messages':messages, 'message_date': cleaned})
    df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %I:%M %p - ")
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_messages']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_messages'], inplace=True)


    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['only_date'] = df['date'].dt.date
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['day_name'] = df['date'].dt.day_name()
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        start_hour_12 = (hour % 12) or 12
        end_hour_12 = ((hour + 1) % 12) or 12
        start_meridiem = 'AM' if hour < 12 else 'PM'
        end_meridiem = 'AM' if (hour + 1) < 12 else 'PM'

        period.append(f"{start_hour_12} {start_meridiem} - {end_hour_12} {end_meridiem}")

    df['period'] = period


    return df


