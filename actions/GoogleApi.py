from __future__ import print_function
from calendar import calendar

import datetime
from re import search
from dateutil import tz
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class Calendar():
    def __init__(self):
        self.service = build('calendar', 'v3', credentials = self.getCredentials())
        self.zone = tz.gettz('America/Argentina/Buenos_Aires')

    def getCredentials(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'F:/rasa_chat/actions/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def getEvents(self, time = None):
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            if time:
                now = time

            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
            if not events:
                return

            return events

        except HttpError as error:
            print('An error occurred: %s' % error)

  
    def getEventById(self, event_id):
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            return event

        except HttpError as error:
            print('An error occurred: %s' % error)

    def createEvent(self, summary, description, startTime, endTime):

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': startTime,

            },
            'end': {
                'dateTime': endTime,
            },
            "visibility": "public",
        }

        event = self.service.events().insert(calendarId='primary', body=event).execute()
        return event

    def available(self, day, time):
        busy = False
        nowTime = datetime.datetime.now()
        year = nowTime.year
        month = nowTime.month
        searchDay = datetime.datetime(year, month, day, tzinfo=self.zone).isoformat()
        events = self.getEvents(searchDay)

        for event in events:
            start = event["start"]["dateTime"]
            dateStart = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")

            end = event["start"]["dateTime"]
            dateEnd = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z")
            if (time >= dateStart.hour and time < dateEnd.hour):
                busy = True
                break
        return busy


    def saveMeet(self, event):
        nowTime = datetime.datetime.now()
        year = nowTime.year
        month = nowTime.month
        startTime = datetime.datetime(year, month, event.get("day"), event.get("hour"), tzinfo=self.zone)
        endTime = startTime + datetime.timedelta(hours=1)

        event = self.createEvent(event.get("summary"), event.get("description"), startTime.isoformat(), endTime.isoformat())
        return event

    def addParticipant(self, event_id, participant):
        event = self.getEventById(event_id)
        print("event", event)
        event["description"] = event["description"] + f", {participant}"
        updated_event = self.service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event