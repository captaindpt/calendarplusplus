import React, { useEffect, useState } from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import ICAL from 'ical.js';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './CalendarView.css';

const localizer = momentLocalizer(moment);

const BACKEND_URL = 'http://localhost:8001';

const CalendarView = ({ icsContent }) => {
  const [events, setEvents] = useState([]);

  const logIcsProcessing = async (type, data) => {
    try {
      const timestamp = new Date().toISOString();
      const logEntry = {
        timestamp,
        type: `ics_${type}`,
        data: JSON.parse(JSON.stringify(data)) // Ensure data is serializable
      };

      console.log('Sending log entry:', logEntry);
      
      const response = await fetch(`${BACKEND_URL}/api/log`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(logEntry)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Failed to log ICS processing:', {
          status: response.status,
          statusText: response.statusText,
          error: errorText
        });
      }
    } catch (error) {
      console.error('Error logging ICS processing:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
    }
  };

  useEffect(() => {
    if (!icsContent) {
      console.log('No ICS content provided');
      return;
    }

    try {
      // Log initial ICS content
      logIcsProcessing('input', { content: icsContent });
      console.log('Parsing ICS content:', icsContent);
      
      // Parse ICS content
      const jcalData = ICAL.parse(icsContent);
      logIcsProcessing('parsed_jcal', { jcalData });
      console.log('Parsed JCAL data:', jcalData);
      
      const vcalendar = new ICAL.Component(jcalData);
      const vevents = vcalendar.getAllSubcomponents('vevent');
      logIcsProcessing('found_events', { count: vevents.length });
      console.log('Found events:', vevents.length);

      // Convert ICAL events to calendar events
      const calendarEvents = vevents.map(vevent => {
        const event = new ICAL.Event(vevent);
        logIcsProcessing('processing_event', { 
          summary: event.summary,
          isRecurring: event.isRecurring()
        });
        console.log('Processing event:', event.summary);
        
        // Get start and end dates
        const startDate = event.startDate.toJSDate();
        const endDate = event.endDate.toJSDate();
        const duration = endDate.getTime() - startDate.getTime();
        
        const eventDates = {
          summary: event.summary,
          start: startDate,
          end: endDate,
          isRecurring: event.isRecurring()
        };
        logIcsProcessing('event_dates', eventDates);
        console.log('Event dates:', eventDates);

        // Handle recurring events
        if (event.isRecurring()) {
          const events = [];
          const recur = event.iterator();
          let next;

          // Get semester start and end dates from the RRULE
          const rrule = event.component.getFirstPropertyValue('rrule');
          const until = rrule.until ? moment(rrule.until.toJSDate()) : moment().add(4, 'months');
          
          const recurringDetails = {
            summary: event.summary,
            rrule: rrule.toString(),
            until: until.format()
          };
          logIcsProcessing('recurring_event', recurringDetails);
          console.log('Recurring event details:', recurringDetails);

          // Generate occurrences until the end date
          while ((next = recur.next()) && moment(next.toJSDate()).isSameOrBefore(until)) {
            const start = next.toJSDate();
            const end = new Date(start.getTime() + duration);

            events.push({
              title: event.summary,
              start,
              end,
              location: event.location || '',
              description: event.description || '',
              allDay: event.startDate.isDate
            });
          }
          
          logIcsProcessing('generated_occurrences', { 
            summary: event.summary, 
            count: events.length 
          });
          console.log(`Generated ${events.length} occurrences for ${event.summary}`);
          return events;
        }

        // Handle single events
        const singleEvent = [{
          title: event.summary,
          start: startDate,
          end: endDate,
          location: event.location || '',
          description: event.description || '',
          allDay: event.startDate.isDate
        }];
        logIcsProcessing('single_event', singleEvent[0]);
        return singleEvent;
      });

      // Flatten array and sort by start date
      const flattenedEvents = calendarEvents.flat().sort((a, b) => a.start - b.start);
      logIcsProcessing('final_events', { 
        count: flattenedEvents.length,
        events: flattenedEvents
      });
      console.log('Final processed events:', flattenedEvents);
      setEvents(flattenedEvents);
    } catch (error) {
      logIcsProcessing('error', { 
        error: error.message,
        stack: error.stack
      });
      console.error('Error parsing ICS content:', error);
      console.log('Raw ICS content:', icsContent);
    }
  }, [icsContent]);

  // Add debug output for render
  console.log('Rendering calendar with events:', events);

  const eventStyleGetter = (event) => {
    return {
      style: {
        backgroundColor: '#007bff',
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: 'none',
        display: 'block',
        overflow: 'hidden'
      }
    };
  };

  const EventComponent = ({ event }) => (
    <div className="calendar-event">
      <div className="event-title">{event.title}</div>
      {event.location && <div className="event-location">{event.location}</div>}
    </div>
  );

  const formats = {
    eventTimeRangeFormat: ({ start, end }, culture, local) =>
      `${local.format(start, 'h:mm a')} - ${local.format(end, 'h:mm a')}`,
  };

  return (
    <div className="calendar-view">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        eventPropGetter={eventStyleGetter}
        components={{
          event: EventComponent
        }}
        formats={formats}
        views={['month', 'week', 'day']}
        defaultView="week"
        tooltipAccessor={event => 
          `${event.title}${event.location ? `\nLocation: ${event.location}` : ''}${event.description ? `\n${event.description}` : ''}`
        }
        popup
        selectable
      />
    </div>
  );
};

export default CalendarView; 