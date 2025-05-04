import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');

  const handleSubmit = async (e) => {
    console.log("Form submitted with query:", query);  // Add this
    e.preventDefault();

    if (!query.trim()) return;

    const userMessage = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMessage]);

    try {
      const res = await fetch('http://172.27.152.214:3000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await res.json();
      const botMessage = { sender: 'bot', text: data.response || "No response." };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setMessages(prev => [...prev, { sender: 'bot', text: '⚠️ Error contacting agent' }]);
    }

    setQuery('');
  };

  return (
    <div className="app">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <strong>{msg.sender === 'user' ? 'You' : 'Agent'}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Type your question..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;
