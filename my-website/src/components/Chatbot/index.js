import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext'; // Added this import
import styles from './styles.module.css';

const Chatbot = () => {
  // Access site configuration from Docusaurus context
  const { siteConfig } = useDocusaurusContext();
  const { customFields } = siteConfig;

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI assistant for Physical AI & Humanoid Robotics. How can I help you today?", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Generate a session ID for the conversation
  const [sessionId] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('chatbot-session-id') || `session-${Date.now()}`;
    }
    return `session-${Date.now()}`;
  });

  // Save session ID to localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('chatbot-session-id', sessionId);
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input; // Capture input before clearing
    setInput('');
    setLoading(true);

    try {
      // Determine API URL using customFields instead of process.env
      const isDev = typeof window !== 'undefined' &&
                    (window.location.hostname === 'localhost' ||
                     window.location.hostname === '127.0.0.1');

      const apiUrl = isDev
        ? 'http://127.0.0.1:8000/api/v1/chat' 
        : customFields.NEXT_PUBLIC_API_URL; // Pulls from docusaurus.config.js

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          session_id: sessionId,
          top_k: 5
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        text: data.response || "I couldn't process your request. Please try again.",
        sender: 'bot'
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting to the server. Please try again later.",
        sender: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.chatbot}>
      {isOpen ? (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <h3>AI Assistant</h3>
            <button 
              className={styles.closeButton} 
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className={styles.chatMessages}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.message} ${styles[message.sender]}`}
              >
                <div className={styles.markdown}>
                  <ReactMarkdown>
                    {message.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.bot}`}>
                <div className={styles.typingIndicator}>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                  <div className={styles.dot}></div>
                </div>
              </div>
            )}
          </div>
          <div className={styles.chatInputArea}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about Physical AI & Humanoid Robotics..."
              className={styles.textInput}
              rows={1}
              disabled={loading}
            />
            <button 
              onClick={handleSend} 
              disabled={!input.trim() || loading}
              className={styles.sendButton}
              aria-label="Send message"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      ) : (
        <button 
          className={styles.floatingButton} 
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          💬
        </button>
      )}
    </div>
  );
};

export default Chatbot;