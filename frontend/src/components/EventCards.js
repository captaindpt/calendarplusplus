import React from 'react';
import './EventCards.css';

function EventCards({ events }) {
  return (
    <div className="event-cards">
      {events.map((event, index) => (
        <div key={index} className="event-card">
          <h3>{event.summary}</h3>
          <p>Start: {new Date(event.startDateTime).toLocaleString()}</p>
          <p>End: {new Date(event.endDateTime).toLocaleString()}</p>
          <p>Description: {event.description}</p>
          <p>Location: {event.location}</p>
        </div>
      ))}
    </div>
  );
}

export default EventCards;