# Calendar++

Simply speak your schedule, and get a calendar file. This tool converts your natural speech about class schedules, meetings, or any recurring events into a standard calendar file that works with Google Calendar, Apple Calendar, or any other calendar app.

For example, you can say:
"I have Database Systems on Mondays and Wednesdays from 2 PM to 3:30 PM in Room 405"
or
"My Algorithms class meets every Tuesday and Thursday at 11 AM until 12:30 PM in the Engineering Building"

Note: This project focuses on the backend processing of voice-to-calendar conversion. While originally planned as a full application, we found that the core voice processing functionality was the most valuable part.

## Features

- **Voice Input**: Just speak your schedule naturally
- **Text Input**: Or type it if you prefer
- **Smart Understanding**: Handles natural language descriptions of your schedule
- **Calendar Files**: Creates standard ICS files you can import anywhere

## How It Works

The system processes your input in these steps:

1. **Voice to Text**
   - Records your voice
   - Converts it to text using Whisper API

2. **Schedule Understanding**
   - Processes your natural description
   - Figures out times, days, and patterns

3. **Event Creation**
   - Creates proper calendar events
   - Handles details like:
     - Class/meeting names
     - Start and end times
     - Locations
     - Weekly patterns

4. **Calendar File**
   - Makes a standard calendar file
   - Ready to import into your preferred calendar app

## Technical Details

### Backend
- Python 3.12+
- Flask
- OpenAI API (GPT-4 and Whisper)
- icalendar for calendar files

### Main Libraries
- `instructor`: OpenAI API handling
- `pydantic`: Data validation
- `icalendar`: Calendar file creation
- `flask-cors`: API access
- `python-dotenv`: Configuration

## Calendar Support

Works with semester schedules (Sept 5 - Nov 27, 2024) and handles:
- One-time events
- Weekly recurring events
- Multiple-day events
- Room locations
- Event descriptions

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

```bash
python -c "
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
"
```

Import the generated `my_schedule.ics` file into your calendar, and you're done!
