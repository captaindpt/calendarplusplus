import React, { useState } from 'react';
import './InputArea.css';

function InputArea({ onSubmit }) {
  const [input, setInput] = useState('');

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = () => {
    onSubmit(input);
    setInput('');
  };

  const handleMicClick = () => {
    // Implement audio input functionality here
    console.log('Mic clicked');
  };

  return (
    <div className="input-area">
      <textarea
        value={input}
        onChange={handleInputChange}
        placeholder="Enter your schedule description..."
        rows={Math.max(2, input.split('\n').length)}
      />
      <div className="button-area">
        <button onClick={handleMicClick} className="mic-button">🎤</button>
        <button onClick={handleSubmit} className="send-button">Send</button>
      </div>
    </div>
  );
}

export default InputArea;