from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import List
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import logging
import logging.handlers
import os
import uuid
import json

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Set up file handler with rotation
log_file = os.path.join(log_dir, 'schedule_processor.log')
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(levelname)s: %(message)s'
))

# Configure logger
logger = logging.getLogger('schedule_processor')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class ClassSchedule(BaseModel):
    """Simple class schedule with just what we need for calendar events"""
    class_name: str = Field(description="Name of the class")
    days: List[str] = Field(description="Days of the week the class meets")
    start_time: str = Field(description="Start time in 24h format (HH:MM)")
    end_time: str = Field(description="End time in 24h format (HH:MM)")
    location: str = Field(description="Location of the class")

class ScheduleProcessor:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info("Initialized ScheduleProcessor")
        
    async def parse_schedule(self, user_input: str) -> List[ClassSchedule]:
        """Extract class schedules from user input using a single LLM call"""
        logger.info("Starting schedule parsing")
        logger.debug(f"Input text: {user_input}")
        
        today = datetime.now()
        semester_end = today + timedelta(days=90)  # Roughly a semester
        logger.debug(f"Using date range: {today.date()} to {semester_end.date()}")
        
        system_prompt = f"""You are a schedule parser that extracts class information for calendar generation.
        Today's date: {today.strftime('%Y-%m-%d')}
        Semester runs until: {semester_end.strftime('%Y-%m-%d')}
        
        Extract only the essential details needed for creating calendar events:
        - Exact class names as mentioned
        - Days they meet (full day names: Monday, Tuesday, etc.)
        - Start and end times (in 24-hour format HH:MM)
        - Locations exactly as specified
        
        Return the information in this format:
        {{
            "classes": [
                {{
                    "class_name": "Database Systems",
                    "days": ["Monday", "Wednesday"],
                    "start_time": "14:00",
                    "end_time": "15:30",
                    "location": "Engineering Building 405"
                }}
            ]
        }}"""

        try:
            logger.debug("Making GPT request")
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                response_format={ "type": "json_object" },
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.debug(f"GPT response: {result}")
            
            parsed = ClassSchedule.model_validate_json(result)
            logger.info(f"Successfully parsed {len(parsed.classes)} classes")
            return parsed.classes
            
        except Exception as e:
            logger.error(f"Error parsing schedule: {str(e)}", exc_info=True)
            raise Exception("Failed to understand the schedule. Please try rephrasing.")

    def generate_ics(self, classes: List[ClassSchedule]) -> str:
        """Convert class schedules directly to ICS format"""
        logger.info("Starting ICS generation")
        logger.debug(f"Generating ICS for {len(classes)} classes")
        
        cal = Calendar()
        cal.add('version', '2.0')
        cal.add('prodid', '-//Calendar++//Schedule Generator//EN')
        
        today = datetime.now()
        semester_end = today + timedelta(days=90)
        logger.debug(f"Using date range: {today.date()} to {semester_end.date()}")
        
        # Map day names to iCal day codes
        day_map = {
            "Monday": "MO",
            "Tuesday": "TU",
            "Wednesday": "WE",
            "Thursday": "TH",
            "Friday": "FR"
        }
        
        for class_schedule in classes:
            try:
                event = Event()
                
                # Create unique ID
                event_uid = str(uuid.uuid4())
                event.add('uid', event_uid)
                event.add('summary', class_schedule.class_name)
                event.add('location', class_schedule.location)
                
                # Set start and end times
                start_hour, start_minute = map(int, class_schedule.start_time.split(':'))
                end_hour, end_minute = map(int, class_schedule.end_time.split(':'))
                
                start_dt = today.replace(hour=start_hour, minute=start_minute)
                end_dt = today.replace(hour=end_hour, minute=end_minute)
                
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                
                # Add weekly recurrence
                recur = {
                    'freq': 'weekly',
                    'until': semester_end,
                    'byday': [day_map[day] for day in class_schedule.days]
                }
                event.add('rrule', recur)
                
                cal.add_component(event)
                logger.debug(f"Added event {event_uid} for {class_schedule.class_name}")
                
            except Exception as e:
                logger.error(f"Error creating event for {class_schedule.class_name}: {str(e)}", exc_info=True)
                raise
        
        logger.info("Successfully generated ICS calendar")
        return cal.to_ical().decode('utf-8')

    async def process_user_schedule(self, user_input: str) -> str:
        """Main processing function: text -> parse -> ICS"""
        logger.info("Starting schedule processing")
        try:
            # One step to parse
            classes = await self.parse_schedule(user_input)
            logger.debug(f"Parsed classes: {json.dumps([c.model_dump() for c in classes], indent=2)}")
            
            # One step to generate ICS
            result = self.generate_ics(classes)
            logger.info("Successfully completed schedule processing")
            return result
            
        except Exception as e:
            logger.error(f"Error processing schedule: {str(e)}", exc_info=True)
            raise