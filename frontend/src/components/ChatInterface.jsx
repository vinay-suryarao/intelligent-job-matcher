import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Bot, User, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../services/api';

const TypingMessage = ({ content, isTyping, onComplete }) => {
  const [displayedContent, setDisplayedContent] = useState('');

  useEffect(() => {
    if (!isTyping) {
      setDisplayedContent(content);
      return;
    }

    // Speed up: Split by newlines (or chunks) instead of characters
    const chunks = content.split('\n');
    let index = 0;

    const interval = setInterval(() => {
      if (index <= chunks.length) {
        // Join the chunks up to the current index
        setDisplayedContent(chunks.slice(0, index).join('\n'));
        index++;
      } else {
        clearInterval(interval);
        if (onComplete) onComplete();
      }
    }, 30); // Fast line-by-line reveal

    return () => clearInterval(interval);
  }, [content, isTyping, onComplete]);

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" className="underline font-medium hover:text-blue-500" />,
        p: ({ node, ...props }) => <p {...props} className="mb-2 last:mb-0" />,
        ul: ({ node, ...props }) => <ul {...props} className="list-disc ml-4 mb-2" />,
        ol: ({ node, ...props }) => <ol {...props} className="list-decimal ml-4 mb-2" />,
        li: ({ node, ...props }) => <li {...props} className="mb-1" />
      }}
    >
      {displayedContent}
    </ReactMarkdown>
  );
};

const ChatInterface = ({ onClose }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI career assistant. I can help you find jobs, improve your resume, and answer career-related questions. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleTypingComplete = (index) => {
    setMessages(prev => prev.map((msg, i) =>
      i === index ? { ...msg, isTyping: false } : msg
    ));
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send history along with the new message
      // Filter out typing markers or failed messages if needed
      const history = messages.map(({ role, content }) => ({ role, content }));

      const response = await api.sendChatMessage(input, history);
      const content = response?.response || response?.message || 'I apologize, I couldn\'t process that. Please try again.';

      const assistantMessage = {
        role: 'assistant',
        content: content,
        isTyping: true
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-2xl h-[600px] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-brand-dark p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-brand-accent rounded-xl flex items-center justify-center">
              <Bot className="text-white" size={24} />
            </div>
            <div>
              <h3 className="text-white font-bold">Career Assistant</h3>
              <p className="text-white/60 text-xs">Powered by AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/60 hover:text-white transition p-2 hover:bg-white/10 rounded-xl"
          >
            <X size={20} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-brand-accent' : 'bg-brand-dark'
                }`}>
                {msg.role === 'user' ? (
                  <User className="text-white" size={16} />
                ) : (
                  <Bot className="text-white" size={16} />
                )}
              </div>
              <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user'
                ? 'bg-brand-accent text-white rounded-tr-none'
                : 'bg-white text-gray-800 rounded-tl-none shadow-sm border border-gray-100'
                }`}>
                <div className={`text-sm leading-relaxed prose prose-sm max-w-none ${msg.role === 'user' ? 'prose-invert text-white' : 'text-gray-800'
                  }`}>
                  {msg.role === 'assistant' ? (
                    <TypingMessage
                      content={msg.content}
                      isTyping={msg.isTyping}
                      onComplete={() => handleTypingComplete(idx)}
                    />
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        a: ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" className="underline font-medium hover:text-blue-500" />,
                        p: ({ node, ...props }) => <p {...props} className="mb-2 last:mb-0" />,
                        ul: ({ node, ...props }) => <ul {...props} className="list-disc ml-4 mb-2" />,
                        ol: ({ node, ...props }) => <ol {...props} className="list-decimal ml-4 mb-2" />,
                        li: ({ node, ...props }) => <li {...props} className="mb-1" />
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-brand-dark rounded-lg flex items-center justify-center">
                <Bot className="text-white" size={16} />
              </div>
              <div className="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-gray-100">
                <Loader2 className="animate-spin text-brand-accent" size={20} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about jobs, careers..."
              className="flex-1 bg-gray-100 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-accent/20 transition"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-brand-dark hover:bg-brand-accent disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition flex items-center gap-2"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
