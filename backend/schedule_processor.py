import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List
from icalendar import Calendar, Event
import asyncio
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ClarifiedSchedule(BaseModel):
    clarified_text: str = Field(description="A clear, structured version of the user's input")

class EventDescription(BaseModel):
    description: str = Field(description="A clear description of a single event")

class ICSEvent(BaseModel):
    summary: str
    start_datetime: datetime
    end_datetime: datetime
    description: str = ""
    location: str = ""
    frequency: str = ""
    days: List[str] = []

class ScheduleProcessor:
    def __init__(self, api_key: str):
        self.client = instructor.patch(AsyncOpenAI(api_key=api_key))
        self.reference_date = self.get_current_date()

    def get_current_date(self) -> str:
        return date.today().isoformat()

    async def transcribe_audio(self, audio_file_path: str) -> str:
        logger.debug(f"Transcribing audio file: {audio_file_path}")
        with open(audio_file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        logger.debug(f"Transcription completed: {transcript}")
        return transcript

    async def clarify_text(self, user_input: str) -> ClarifiedSchedule:
        logger.debug(f"Clarifying text: {user_input}")
        result = await self.client.chat.completions.create(
            model="gpt-4",
            response_model=ClarifiedSchedule,
            messages=[
                {"role": "system", "content": f"You are an AI assistant that clarifies and structures unorganized schedule descriptions. Today's date is {self.reference_date}. Provide a clear, organized version of the user's input, interpreting relative dates based on the current date."},
                {"role": "user", "content": f"Clarify and structure this schedule description: {user_input}"}
            ],
            max_retries=2
        )
        logger.debug(f"Clarified text: {result.clarified_text}")
        return result

    async def split_into_events(self, clarified_text: str) -> List[EventDescription]:
        logger.debug(f"Splitting into events: {clarified_text}")
        result = await self.client.chat.completions.create(
            model="gpt-4",
            response_model=List[EventDescription],
            messages=[
                {"role": "system", "content": f"You are an AI assistant that splits a clarified schedule into individual event descriptions. Today's date is {self.reference_date}. Each event should be a separate item have specified the name of the event, description of the event, the start date, the end date, the frequency of the event."},
                {"role": "user", "content": f"Split this schedule into individual events: {clarified_text}"}
            ],
            max_retries=2
        )
        logger.debug(f"Split events: {result}")
        return result

    async def convert_to_ics_event(self, event_description: str) -> ICSEvent:
        logger.debug(f"Converting to ICS event: {event_description}")
        result = await self.client.chat.completions.create(
            model="gpt-4",
            response_model=ICSEvent,
            messages=[
                {"role": "system", "content": f"""You are an AI assistant that converts event descriptions into structured ICS event data. Today's date is {self.reference_date}. Provide the necessary details for an ICS event, using specific dates based on the current date. Use ISO format for dates and times (YYYY-MM-DDTHH:MM:SS).

                    For recurring events:
                    1. Specify the frequency as one of DAILY, WEEKLY, MONTHLY, or YEARLY.
                    2. For the 'days' field, provide a list of individual day abbreviations. Use these exact abbreviations: MO, TU, WE, TH, FR, SA, SU.

                    Example of correct 'days' format: ["MO", "WE", "FR"] for Monday, Wednesday, Friday.

                    Do not combine day abbreviations into a single string."""},
                {"role": "user", "content": f"Convert this event description to ICS event data: {event_description}"}
            ],
            max_retries=2
        )
        logger.debug(f"Converted ICS event: {result}")
        return result

    def generate_ics(self, ics_events: List[ICSEvent]) -> str:
        logger.debug(f"Generating ICS file for {len(ics_events)} events")
        cal = Calendar()
        for event in ics_events:
            ics_event = Event()
            ics_event.add('summary', event.summary)
            ics_event.add('dtstart', event.start_datetime)
            ics_event.add('dtend', event.end_datetime)
            ics_event.add('description', event.description)
            if event.location:
                ics_event.add('location', event.location)
            if event.frequency:
                rrule = {'freq': event.frequency.upper()}
                if event.days:
                    # Filter valid days and join them into a comma-separated string
                    valid_days = [day for day in event.days if day in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']]
                    print(valid_days)
                    if valid_days:
                        rrule['byday'] = (valid_days)  # Join as a string
                ics_event.add('rrule', rrule)
            cal.add_component(ics_event)

        ics_content = cal.to_ical().decode('utf-8')
        logger.debug(f"Generated ICS content: {ics_content}")
        return ics_content

    async def process_user_schedule(self, user_input: str) -> str:
        logger.info(f"Processing user schedule: {user_input}")

        # Step 1: Clarify the general text
        clarified_schedule = await self.clarify_text(user_input)

        # Step 2: Split into individual event descriptions
        event_descriptions = await self.split_into_events(clarified_schedule.clarified_text)

        # Step 3: Convert each event description to ICS event
        ics_events = []
        for event_desc in event_descriptions:
            ics_event = await self.convert_to_ics_event(event_desc.description)
            ics_events.append(ics_event)

        # Generate .ics file
        ics_content = self.generate_ics(ics_events)

        logger.info("Schedule processing completed")
        return ics_content


import asyncio
import os
from schedule_processor import ScheduleProcessor
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    env_path = Path('..') / '.env'
    load_dotenv(dotenv_path=env_path)
    # Get the API key from an environment variable
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logger.error("Please set the OPENAI_API_KEY environment variable.")
        return

    # Initialize the ScheduleProcessor
    processor = ScheduleProcessor(api_key)

    # Get user input
    print("Please enter your schedule description:")
    user_input = input()

    try:
        # Process the schedule
        ics_content = await processor.process_user_schedule(user_input)

        # Save the ICS content to a file
        with open('output_schedule.ics', 'w') as f:
            f.write(ics_content)

        logger.info("Schedule processed successfully!")
        logger.info("ICS file saved as 'output_schedule.ics'")

        # Print the ICS content for inspection
        logger.debug("ICS Content:")
        logger.debug(ics_content)

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
