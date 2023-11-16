from __future__ import print_function

import psutil
import sqlite3

import time
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("Application working")
    
    #store applications to be watched
    watched_applications = ['cs2.exe', 'Notepad.exe']
    #create dictionary to store information about the apps in watched applications
    process_info = {app: {'start_time': None, 'start_times_list':[], 'last_end_time': None} for app in watched_applications}
    #set duration in which it will wait to detect is an application is reloaded in (seconds)
    duration = 30
    
    try:
        #created loop condition
        while True:
            #for the apps in watched applications
            for app in watched_applications:
                #iterate through the process detected by psutil and check if any are apps watched
                if any(p.name() == app for p in psutil.process_iter(['pid', 'name'])):
                    #if the app doesnt have a start time
                    if process_info[app]['start_time'] is None:
                        #set start time to current time
                        start_time = datetime.datetime.utcnow()
                        process_info[app]['start_time'] = start_time
                        #create a list of start times so if app is opened multiple times all times can be accessed
                        process_info[app]['start_times_list'].append(start_time) 
                        print(f"{app} started at {start_time}")
                else:
                    #if the app has a start time
                    if process_info[app]['start_time'] is not None:
                        #set end time to current time
                        end_time = datetime.datetime.utcnow()
                        #if app doesnt have an end time
                        if process_info[app]['last_end_time'] is None:
                            #set end time to current time on app close
                            process_info[app]['last_end_time'] = end_time
                            #start timer
                            timer_start = time.time()
                            #calculate end time for the timer
                            timer_end = timer_start + duration 
                            #while not at the end of timer
                            while time.time() < timer_end:
                                #if the app is detected as reloaded
                                if any(p.name() == app for p in psutil.process_iter(['pid', 'name'])):
                                    print("App opened, waiting for app to close again")
                                    #exit loop if the app is reopened
                                    break  
                                time.sleep(1)
                            else:
                                #if app isnt reopened meaning end of a session
                                #event creation after waiting
                                createEvent(creds, app, process_info[app]['start_times_list'][0], end_time)
                                addData(app, process_info[app]['start_times_list'][0], end_time)  
                                #reset values for the apps so they can be detected if reopened
                                process_info[app]['start_times_list'] = []
                            process_info[app]['last_end_time'] = None 
                        process_info[app]['start_time'] = None
            time.sleep(1)
        
    except HttpError as error:
        print('An error occurred: %s' % error)

# Function to create google calander event
# creds - google calander users credentials, desc - app detected by psutil
# startTime and endTime - times application was started and ended
def createEvent(creds, desc, startTime, endTime):
    # specific format for creating an event on google calendar
    event = {
            'summary': desc,
            'start': {
                # formating startTime
                'dateTime': startTime.isoformat() + 'Z',
                'timeZone': 'Europe/London',
            },
            'end': {
                # formatting endTime
                'dateTime': endTime.isoformat() + 'Z',
                'timeZone': 'Europe/London',
            }
        }
    
    # Adding the event to google calendar
    service = build('calendar', 'v3', credentials=creds)
    event = service.events().insert(calendarId = 'primary', body = event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# Function to create database input
# application - detected from psutil, startTime and endTime - times application was started and ended
def addData(application, startTime, endTime):
    try:
        con = sqlite3.connect("timetable.db")
        cur = con.cursor()
        # Calulate the duarion the app was opened in hours
        duration = (endTime - startTime).total_seconds() / 3600
        
        # Creating the insert
        insert = (application, 'samal', "{:.2f}".format(duration), 'automatic')
        # executing the insert in desired table in database
        cur.execute("INSERT INTO time (application, user, duration, type) VALUES(?, ?, ?, ?)", insert)
        # committing the insert to the database
        con.commit()
        cur.close()
    
    # Print any errors that occured during insert
    except sqlite3.Error as error:
        print("Error: ", error)
    
    # After insert close connection to the database
    finally:
        if con:
            con.close()

if __name__ == '__main__':
    main()