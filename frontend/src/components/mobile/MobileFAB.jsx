import React, { useState } from 'react';
import { Plus, X, FileText, BarChart3, MessageSquare } from 'lucide-react';
import Button from '../ui/Button';

const MobileFAB = ({
  onCreateSpreadsheet,
  onModeChange,
  currentMode,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const quickActions = [
    {
      id: 'dpr',
      label: 'DPR',
      icon: FileText,
      description: 'Update DPR'
    },
    {
      id: 'dlr',
      label: 'DLR',
      icon: BarChart3,
      description: 'Update DLR'
    },
    {
      id: 'logs',
      label: 'Logs',
      icon: MessageSquare,
      description: 'Analyze Logs'
    }
  ];

  const handleMainClick = () => {
    if (isExpanded) {
      setIsExpanded(false);
    } else {
      onCreateSpreadsheet();
    }
  };

  const handleQuickAction = (actionId) => {
    onModeChange(actionId);
    setIsExpanded(false);
  };

  return (
    <div className={`fixed bottom-20 right-4 z-40 ${className}`}>
      {/* Quick Actions */}
      {isExpanded && (
        <div className="flex flex-col gap-3 mb-4 animate-slide-up">
          {quickActions.map((action) => {
            const Icon = action.icon;
            const isActive = currentMode === action.id;
            
            return (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action.id)}
                className={`w-12 h-12 rounded-full shadow-lg transition-all duration-200 flex items-center justify-center ${
                  isActive
                    ? 'bg-primary-600 text-white scale-110'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
                title={action.description}
              >
                <Icon className="w-5 h-5" />
              </button>
            );
          })}
        </div>
      )}
      
      {/* Main FAB */}
      <Button
        onClick={handleMainClick}
        variant="primary"
        size="lg"
        className="w-14 h-14 rounded-full shadow-lg hover:shadow-xl transition-all duration-200"
      >
        {isExpanded ? (
          <X className="w-6 h-6" />
        ) : (
          <Plus className="w-6 h-6" />
        )}
      </Button>
    </div>
  );
};

export default MobileFAB;
