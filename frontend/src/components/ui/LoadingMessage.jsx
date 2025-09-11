import React from 'react';
import { Bot } from 'lucide-react';

const LoadingMessage = ({ mode = 'dpr' }) => {
  const getModeText = () => {
    switch (mode) {
      case 'dpr':
        return 'AI is analyzing your progress...';
      case 'dlr':
        return 'AI is processing your activities...';
      case 'logs':
        return 'AI is analyzing your data...';
      default:
        return 'AI is thinking...';
    }
  };

  return (
    <div className="flex gap-3 justify-start animate-fade-in-up">
      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-primary-600 animate-pulse-soft" />
      </div>
      
      <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md shadow-soft px-6 py-4">
        <div className="flex items-center space-x-2 mb-3">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className="text-xs text-gray-500 font-medium">{getModeText()}</span>
        </div>
        
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded loading-shimmer"></div>
          <div className="h-4 bg-gray-200 rounded loading-shimmer w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded loading-shimmer w-1/2"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingMessage;
