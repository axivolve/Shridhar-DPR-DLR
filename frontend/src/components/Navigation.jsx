import React from 'react';
import { FileText, Plus, Calendar, Users } from 'lucide-react';

const Navigation = ({ sheets = [], selectedSheet, onSheetSelect, onCreateSpreadsheet }) => {
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return 'Unknown date';
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Your Spreadsheets</h2>
        <button
          onClick={onCreateSpreadsheet}
          className="w-full btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create New Month
        </button>
      </div>

      {/* Sheets List */}
      <div className="flex-1 overflow-y-auto">
        {!Array.isArray(sheets) ? (
          <div className="p-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-3"></div>
            <p className="text-gray-600 text-sm">Loading spreadsheets...</p>
          </div>
        ) : sheets.length === 0 ? (
          <div className="p-4 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-600 text-sm mb-3">No spreadsheets found</p>
            <button
              onClick={onCreateSpreadsheet}
              className="btn-secondary text-sm"
            >
              Create your first spreadsheet
            </button>
          </div>
        ) : (
          <div className="p-2">
            {sheets.map((sheet) => (
              <div
                key={sheet.id}
                onClick={() => onSheetSelect(sheet)}
                className={`p-3 rounded-lg cursor-pointer transition-colors duration-200 mb-2 ${
                  selectedSheet?.id === sheet.id
                    ? 'bg-primary-50 border border-primary-200'
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    selectedSheet?.id === sheet.id
                      ? 'bg-primary-100'
                      : 'bg-gray-100'
                  }`}>
                    <FileText className={`w-4 h-4 ${
                      selectedSheet?.id === sheet.id
                        ? 'text-primary-600'
                        : 'text-gray-600'
                    }`} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-medium text-sm truncate ${
                      selectedSheet?.id === sheet.id
                        ? 'text-primary-900'
                        : 'text-gray-900'
                    }`}>
                      {sheet.name}
                    </h3>
                    
                    <div className="flex items-center gap-2 mt-1">
                      <Calendar className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {formatDate(sheet.modifiedTime)}
                      </span>
                    </div>
                    
                    {sheet.owners && sheet.owners.length > 0 && (
                      <div className="flex items-center gap-1 mt-1">
                        <Users className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {sheet.owners[0].displayName}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="text-xs text-gray-500 text-center">
          <p>Total: {sheets.length} spreadsheet{sheets.length !== 1 ? 's' : ''}</p>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
