import React from 'react';
import './EventCards.css';

function EventCards({ events }) {
  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  if (!events || events.length === 0) {
    return null;
  }

  return (
    <div className="event-cards">
      {events.map((event, index) => (
        <div key={index} className="event-card">
          <h3>{event.summary}</h3>
          <p className="datetime">
            <strong>Start:</strong> {formatDateTime(event.startDateTime)}
          </p>
          <p className="datetime">
            <strong>End:</strong> {formatDateTime(event.endDateTime)}
          </p>
          {event.description && (
            <p><strong>Description:</strong> {event.description}</p>
          )}
          {event.location && (
            <p className="location">📍 {event.location}</p>
          )}
        </div>
      ))}
    </div>
  );
}

export default EventCards;