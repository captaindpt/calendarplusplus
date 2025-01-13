import React, { useState } from 'react';
import './InputArea.css';

const InputArea = ({ onSubmit, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(input);
  };

  return (
    <form onSubmit={handleSubmit} className="input-area">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter your class schedule..."
        disabled={disabled}
      />
      <div className="button-area">
        <button type="submit" className="send-button" disabled={disabled}>
          {disabled ? 'Processing...' : 'Process Schedule'}
        </button>
      </div>
    </form>
  );
};

export default InputArea;