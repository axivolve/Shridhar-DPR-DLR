import React from 'react';
import { FileText, MessageSquare, BarChart3, Plus, Settings } from 'lucide-react';
import Button from '../ui/Button';

const BottomNavigation = ({
  activeTab,
  onTabChange,
  onCreateSpreadsheet,
  onSettings,
  className = '',
}) => {
  const tabs = [
    {
      id: 'dpr',
      label: 'DPR',
      icon: FileText,
      description: 'Daily Progress Reports'
    },
    {
      id: 'dlr',
      label: 'DLR',
      icon: BarChart3,
      description: 'Daily Log Reports'
    },
    {
      id: 'logs',
      label: 'Logs',
      icon: MessageSquare,
      description: 'Log Analysis'
    }
  ];

  return (
    <div className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-bottom ${className}`}>
      <div className="flex items-center justify-around px-2 py-2">
        {/* Tab Buttons */}
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-colors duration-200 touch-target ${
                isActive
                  ? 'text-primary-600 bg-primary-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
              title={tab.description}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{tab.label}</span>
            </button>
          );
        })}
        
        {/* Create Button */}
        <Button
          onClick={onCreateSpreadsheet}
          variant="primary"
          size="sm"
          className="rounded-full w-12 h-12 p-0 shadow-lg"
          title="Create New Spreadsheet"
        >
          <Plus className="w-5 h-5" />
        </Button>
        
        {/* Settings Button */}
        <button
          onClick={onSettings}
          className="flex flex-col items-center gap-1 p-2 rounded-lg transition-colors duration-200 touch-target text-gray-500 hover:text-gray-700 hover:bg-gray-50"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
          <span className="text-xs font-medium">Settings</span>
        </button>
      </div>
    </div>
  );
};

export default BottomNavigation;
