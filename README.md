# Calendar++

> **Note**: This is an experimental project in active development, primarily focused on exploring LLM-powered backend processing for natural language schedule understanding. The implementation and features are subject to change.

A test bed for natural language schedule processing using GPT-4, exploring how Large Language Models can understand and structure informal schedule descriptions. The project aims to convert natural language about class schedules into structured calendar data, testing the boundaries of LLM comprehension and data transformation.

Simply describe your schedule, and the system attempts to convert it into a calendar file. For example:
"I have Database Systems on Mondays and Wednesdays from 2 PM to 3:30 PM in Room 405"
or
"My Algorithms class meets every Tuesday and Thursday at 11 AM until 12:30 PM in the Engineering Building"

## Project Focus

This project serves as a research implementation exploring:
- LLM capabilities in understanding unstructured schedule information
- Natural language processing for temporal and location data
- Conversion of semantic understanding into structured data formats
- Balance between model comprehension and validation requirements

## Features

- **Natural Language**: Just describe your schedule in plain English
- **Smart Parsing**: Automatically understands class names, times, days, and locations
- **Calendar Files**: Creates standard ICS files you can import anywhere
- **Dynamic Scheduling**: Creates events starting from today, running for a semester
- **Weekly Patterns**: Handles recurring weekly schedules automatically

## How It Works

The system processes your input in two simple steps:

1. **Schedule Understanding**
   - Takes your natural description
   - Extracts class names, times, days, and locations
   - Uses GPT-4 for accurate understanding

2. **Calendar Creation**
   - Creates proper calendar events
   - Sets up weekly recurrence
   - Generates a standard ICS file

## Technical Details

### Backend
- Python 3.12+
- Flask
- OpenAI API (GPT-4)
- icalendar for calendar files

### Main Libraries
- `openai`: GPT-4 API
- `pydantic`: Data validation
- `icalendar`: Calendar file creation
- `flask-cors`: API access
- `python-dotenv`: Configuration

## Calendar Support

Creates semester-length schedules that:
- Start from today
- Run for roughly 90 days
- Support weekly recurring events
- Include room locations
- Work with all major calendar apps

## Getting Started

1. **Get the code**
   ```bash
   git clone https://github.com/yourusername/calendarplusplus.git
   cd calendarplusplus/backend
   ```

2. **Set up Python**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Add your OpenAI key**
   Create a `.env` file in the backend directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Start it up**
   ```bash
   python app.py
   ```

Try it out with this simple script:

```python
import asyncio
from schedule_processor import ScheduleProcessor

async def main():
    processor = ScheduleProcessor('your_api_key_here')
    # Just describe your schedule naturally
    schedule = 'I have Database class every Monday and Wednesday from 2 PM to 3:30 PM in Room 405'
    result = await processor.process_user_schedule(schedule)
    with open('my_schedule.ics', 'w') as f:
        f.write(result)

asyncio.run(main())
```

Import the generated `my_schedule.ics` file into your calendar, and you're done!

## Implementation Notes

The system uses a streamlined approach:
1. A single GPT-4 call parses the schedule into structured data
2. Direct conversion to ICS format with proper recurrence rules
3. Dynamic date handling starting from today
4. Minimal validation for maximum reliability
5. Clear, focused prompts for consistent results
