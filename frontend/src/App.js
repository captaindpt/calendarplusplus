import React, { useState } from 'react';
import './App.css';
import InputArea from './components/InputArea';
import EventCards from './components/EventCards';

function App() {
  const [events, setEvents] = useState([]);

  const handleSubmit = async (input) => {
    // Here you would call your backend API to process the input
    // For now, let's just simulate it with a timeout
    setTimeout(() => {
      const sampleEvents = [
        { summary: 'Math Class', startDateTime: '2024-09-05T10:00:00', endDateTime: '2024-09-05T12:00:00', description: 'Introduction to Calculus', location: 'Room 101' },
        { summary: 'History Seminar', startDateTime: '2024-09-06T14:00:00', endDateTime: '2024-09-06T16:00:00', description: 'World War II', location: 'Auditorium' },
      ];
      setEvents(sampleEvents);
    }, 2000);
  };

  return (
    <div className="App">
      <h1>Schedule Generator</h1>
      <InputArea onSubmit={handleSubmit} />
      <EventCards events={events} />
    </div>
  );
}

export default App;