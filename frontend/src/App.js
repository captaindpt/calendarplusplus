import React, { useState, useEffect } from "react";
import "./App.css";
import StatusCheck from "./components/StatusCheck";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:8000/api/hello")
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => setMessage("Error fetching message"));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>My React + Flask App</h1>
        <p>{message}</p>
        <StatusCheck />
      </header>
    </div>
  );
}

export default App;
