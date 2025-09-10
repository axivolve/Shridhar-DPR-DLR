import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, BarChart3, MessageSquare, Bot, User, Loader2 } from 'lucide-react';
import { dprAPI, dlrAPI, logsAPI } from '../api';

const ChatInterface = ({ selectedSheet, user }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [mode, setMode] = useState('dpr'); // 'dpr', 'dlr', 'logs'
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const modeOptions = [
    { value: 'dpr', label: 'Update DPR', icon: FileText, description: 'Daily Progress Reports' },
    { value: 'dlr', label: 'Update DLR', icon: BarChart3, description: 'Daily Log Reports' },
    { value: 'logs', label: 'Analyze Logs', icon: MessageSquare, description: 'Log Analysis' },
  ];

  const getPlaceholderText = () => {
    switch (mode) {
      case 'dpr':
        return 'Describe the daily progress updates... (e.g., "Completed foundation work for Block A, 50% progress")';
      case 'dlr':
        return 'Describe the daily log activities... (e.g., "Added 10 cubic meters of concrete to Block B")';
      case 'logs':
        return 'Ask questions about the logs... (e.g., "What was the total concrete used this month?")';
      default:
        return 'Type your message...';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !selectedSheet || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      mode: mode,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      const requestBody = {
        site_engineer_name: user?.name || 'Unknown User',
        phone_number: user?.phone_number || '1234567890',
        users_query: inputMessage,
      };

      if (mode === 'dpr') {
        response = await dprAPI.updateDPR(selectedSheet.id, requestBody);
      } else if (mode === 'dlr') {
        response = await dlrAPI.updateDLR(selectedSheet.id, requestBody);
      } else if (mode === 'logs') {
        response = await logsAPI.analyzeLogs(selectedSheet.id, {
          users_query: inputMessage,
        });
      }

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.data.feedback || response.data.llm_result?.feedback || 'Operation completed successfully',
        timestamp: new Date(),
        mode: mode,
        data: response.data,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: error.response?.data?.detail || 'An error occurred while processing your request',
        timestamp: new Date(),
        mode: mode,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {selectedSheet.name}
            </h2>
            <p className="text-sm text-gray-600">
              AI-powered spreadsheet management
            </p>
          </div>
        </div>

        {/* Mode Selector */}
        <div className="mt-4">
          <div className="flex gap-2">
            {modeOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  onClick={() => setMode(option.value)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                    mode === option.value
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-transparent'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {option.label}
                </button>
              );
            })}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {modeOptions.find(opt => opt.value === mode)?.description}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              {mode === 'dpr' && 'Describe your daily progress updates and I\'ll help you update the DPR sheet.'}
              {mode === 'dlr' && 'Tell me about your daily activities and I\'ll update the DLR sheet with fuzzy matching.'}
              {mode === 'logs' && 'Ask me questions about the log data and I\'ll provide insights and analysis.'}
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.type === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.type !== 'user' && (
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary-600" />
                </div>
              )}
              
              <div
                className={`max-w-[70%] rounded-lg px-4 py-3 ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : message.type === 'error'
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium opacity-75">
                    {message.type === 'user' ? 'You' : 'AI Assistant'}
                  </span>
                  <span className="text-xs opacity-60">
                    {formatTimestamp(message.timestamp)}
                  </span>
                  <span className="text-xs opacity-60">
                    • {modeOptions.find(opt => opt.value === message.mode)?.label}
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>

              {message.type === 'user' && (
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-gray-600" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-primary-600" />
            </div>
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                <span className="text-sm text-gray-600">Processing your request...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={getPlaceholderText()}
              className="input-field"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
