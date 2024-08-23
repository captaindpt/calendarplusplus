import React, { useState, useEffect } from "react";

function StatusCheck() {
  const [status, setStatus] = useState("Checking backend status...");

  useEffect(() => {
    fetch("http://localhost:8000/api/status")
      .then((response) => response.json())
      .then((data) => setStatus(data.status))
      .catch((error) => setStatus("Error connecting to backend"));
  }, []);

  return (
    <div>
      <h2>Backend Status</h2>
      <p>{status}</p>
    </div>
  );
}

export default StatusCheck;
