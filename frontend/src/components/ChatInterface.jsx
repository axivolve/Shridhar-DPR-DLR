import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, BarChart3, MessageSquare, Bot, User, Loader2, Mic, MicOff } from 'lucide-react';
import { dprAPI, dlrAPI, logsAPI } from '../api';
import Button from './ui/Button';
import { Card, CardContent } from './ui/Card';
import LoadingSpinner from './ui/LoadingSpinner';
import MobileFAB from './mobile/MobileFAB';

const ChatInterface = ({ selectedSheet, user }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [mode, setMode] = useState('dpr'); // 'dpr', 'dlr', 'logs'
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const parseSheetTitle = (sheetName) => {
    // Check if it's a DPR sheet
    if (sheetName.startsWith('DPR_')) {
      const withoutPrefix = sheetName.substring(4);
      const parts = withoutPrefix.split('_');
      
      if (parts.length >= 2) {
        const year = parts[parts.length - 1];
        const month = parts[parts.length - 2];
        const projectName = parts.slice(0, -2).join(' ').replace(/-/g, ' ');
        
        // Convert month to proper format
        const monthNames = {
          'JANUARY': 'January', 'FEBRUARY': 'February', 'MARCH': 'March',
          'APRIL': 'April', 'MAY': 'May', 'JUNE': 'June',
          'JULY': 'July', 'AUGUST': 'August', 'SEPTEMBER': 'September',
          'OCTOBER': 'October', 'NOVEMBER': 'November', 'DECEMBER': 'December'
        };
        
        const formattedMonth = monthNames[month.toUpperCase()] || month;
        return {
          project: projectName,
          period: `${formattedMonth} ${year}`,
          isDPR: true
        };
      }
    }
    
    // Fallback for non-DPR sheets
    return {
      project: sheetName,
      period: '',
      isDPR: false
    };
  };

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
        site_engineer_name: user?.name || user?.email || 'Unknown User',
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
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white safe-top">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            {(() => {
              const titleInfo = parseSheetTitle(selectedSheet.name);
              return (
                <>
                  <h2 className="text-lg font-semibold text-gray-900 truncate">
                    {titleInfo.project}
                  </h2>
                  {titleInfo.period && (
                    <p className="text-sm text-gray-600 truncate">
                      {titleInfo.period}
                    </p>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.length === 0 ? (
          <div className="text-center py-12 px-4">
            <div className="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Bot className="w-10 h-10 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              Start a conversation
            </h3>
            <p className="text-gray-600 max-w-md mx-auto text-balance mb-6">
              {mode === 'dpr' && 'Describe your daily progress updates and I\'ll help you update the DPR sheet.'}
              {mode === 'dlr' && 'Tell me about your daily activities and I\'ll update the DLR sheet with fuzzy matching.'}
              {mode === 'logs' && 'Ask me questions about the log data and I\'ll provide insights and analysis.'}
            </p>
            
            {/* Quick action buttons */}
            <div className="flex flex-wrap gap-2 justify-center">
              {modeOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <Button
                    key={option.value}
                    onClick={() => setMode(option.value)}
                    variant={mode === option.value ? 'primary' : 'outline'}
                    size="sm"
                    className="text-xs"
                  >
                    <Icon className="w-4 h-4" />
                    {option.label}
                  </Button>
                );
              })}
            </div>
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
              
              <Card
                className={`max-w-[85%] sm:max-w-[70%] ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white border-primary-600'
                    : message.type === 'error'
                    ? 'bg-error-50 text-error-800 border-error-200'
                    : 'bg-white text-gray-900 border-gray-200'
                }`}
              >
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 mb-2">
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
                  <p className="text-sm whitespace-pre-wrap text-balance">{message.content}</p>
                </CardContent>
              </Card>

              {message.type === 'user' && (
                <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
                  {user?.picture ? (
                    <img 
                      src={user.picture} 
                      alt={user?.name || 'User'} 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                      <User className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
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
            <Card className="bg-white border-gray-200">
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                  <span className="text-sm text-gray-600">Processing your request...</span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white safe-bottom">
        {/* Mode Selector */}
        <div className="mb-4">
          <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
            {modeOptions.map((option) => {
              const Icon = option.icon;
              return (
                <Button
                  key={option.value}
                  onClick={() => setMode(option.value)}
                  variant={mode === option.value ? 'primary' : 'outline'}
                  size="sm"
                  className="flex-shrink-0"
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{option.label}</span>
                </Button>
              );
            })}
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            {modeOptions.find(opt => opt.value === mode)?.description}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={getPlaceholderText()}
              className="input w-full h-12 text-base"
              disabled={isLoading}
            />
          </div>
          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={!inputMessage.trim() || isLoading}
            loading={isLoading}
            className="h-12 px-4"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline ml-2">Send</span>
          </Button>
        </form>
      </div>

      {/* Mobile FAB */}
      {/* <MobileFAB
        onCreateSpreadsheet={() => {
          // This would be passed down from parent component
          console.log('Create spreadsheet from FAB');
        }}
        onModeChange={setMode}
        currentMode={mode}
        className="lg:hidden"
      /> */}
    </div>
  );
};

export default ChatInterface;
