import React, { useState, useRef, useEffect } from 'react';
import InputArea from './components/InputArea';
import CalendarView from './components/CalendarView';
import './App.css';

const BACKEND_URL = 'http://localhost:8001';

const App = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [icsContent, setIcsContent] = useState(null);
  const [rawIcsContent, setRawIcsContent] = useState('');
  const [isDebugMode, setIsDebugMode] = useState(false);
  const [debugLogs, setDebugLogs] = useState([]);
  const debugTerminalRef = useRef(null);

  const addDebugLog = (message, type = 'info') => {
    const timestamp = new Date().toISOString();
    setDebugLogs(logs => [...logs, { timestamp, message, type }]);
  };

  useEffect(() => {
    if (debugTerminalRef.current) {
      debugTerminalRef.current.scrollTop = debugTerminalRef.current.scrollHeight;
    }
  }, [debugLogs]);

  useEffect(() => {
    addDebugLog('Application initialized', 'info');
    addDebugLog('Debug mode is available', 'success');
    addDebugLog('Waiting for user input...', 'info');
  }, []);

  const handleSubmit = async (input) => {
    setLoading(true);
    setError(null);
    setIcsContent(null);
    setRawIcsContent('');
    addDebugLog('Processing new schedule request...', 'info');
    
    if (!input || input.trim().length === 0) {
      const errorMsg = 'Please enter a schedule description';
      setError(errorMsg);
      addDebugLog(errorMsg, 'error');
      setLoading(false);
      return;
    }

    try {
      addDebugLog('Sending request to backend...', 'info');
      const response = await fetch(`${BACKEND_URL}/api/process-schedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ schedule: input.trim() }),
      });

      const data = await response.json();
      addDebugLog('Received response from backend', 'info');
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process schedule');
      }

      setIcsContent(data.ics_content);
      setRawIcsContent(data.ics_content);
      addDebugLog('Successfully processed schedule', 'success');
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
      addDebugLog(`Error: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!icsContent) return;
    addDebugLog('Initiating file download...', 'info');
    
    try {
      const blob = new Blob([icsContent], { type: 'text/calendar' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'schedule.ics';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      addDebugLog('File download completed', 'success');
    } catch (err) {
      addDebugLog(`Download failed: ${err.message}`, 'error');
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Calendar++</h1>
        <p>Convert your class schedule into a calendar file</p>
      </header>

      <main>
        <InputArea onSubmit={handleSubmit} disabled={loading} />
        
        {error && <div className="error-message">{error}</div>}
        
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing your schedule...</p>
          </div>
        )}

        {icsContent && (
          <div className="ics-content">
            <div className="ics-header">
              <h3>Generated Calendar</h3>
              <button className="download-button" onClick={handleDownload}>
                Download ICS File
              </button>
            </div>
            <CalendarView icsContent={icsContent} />
          </div>
        )}

        <div className="debug-section">
          <label className="debug-toggle">
            <input
              type="checkbox"
              checked={isDebugMode}
              onChange={(e) => setIsDebugMode(e.target.checked)}
            />
            Debug Mode
          </label>
          
          {isDebugMode && (
            <div className="debug-content">
              <h4>Debug Terminal</h4>
              <div className="debug-terminal" ref={debugTerminalRef}>
                {debugLogs.map((log, index) => (
                  <div key={index} className={`debug-log debug-${log.type}`}>
                    <span className="debug-timestamp">{log.timestamp}</span>
                    <span className="debug-message">{log.message}</span>
                  </div>
                ))}
              </div>
              
              <div className="debug-info">
                <p><strong>Status:</strong> {loading ? 'Loading' : error ? 'Error' : icsContent ? 'Success' : 'Idle'}</p>
                {error && (
                  <div className="debug-error">
                    <strong>Error Details:</strong>
                    <pre>{error}</pre>
                  </div>
                )}
                {rawIcsContent && (
                  <>
                    <strong>Raw ICS Content:</strong>
                    <pre className="raw-ics">{rawIcsContent}</pre>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;