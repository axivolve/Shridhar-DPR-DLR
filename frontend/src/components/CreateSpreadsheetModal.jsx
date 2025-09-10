import React, { useState } from 'react';
import { X, FileText, Calendar, Building, Loader2 } from 'lucide-react';
import { spreadsheetAPI } from '../api';

const CreateSpreadsheetModal = ({ availableSheets, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    source_spreadsheet_id: '',
    project_name: '',
    month: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const months = [
    'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
    'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.source_spreadsheet_id || !formData.project_name || !formData.month) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Map the form data to match backend expectations
      const requestData = {
        spreadsheet_id: formData.source_spreadsheet_id,
        project_name: formData.project_name,
        month: formData.month.toUpperCase() // Backend expects uppercase month names
      };
      
      console.log('Sending request data:', requestData);
      await spreadsheetAPI.createNewSpreadsheet(requestData);
      onSuccess();
    } catch (error) {
      console.error('Error creating spreadsheet:', error);
      console.error('Error details:', error.response?.data);
      
      // Handle different error response formats
      let errorMessage = 'Failed to create spreadsheet';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(err => err.msg || err).join(', ');
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">
              Create New Spreadsheet
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Source Spreadsheet */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source Spreadsheet
            </label>
            <select
              name="source_spreadsheet_id"
              value={formData.source_spreadsheet_id}
              onChange={handleInputChange}
              className="input-field"
              required
            >
              <option value="">Select a spreadsheet to copy from</option>
              {availableSheets.map((sheet) => (
                <option key={sheet.id} value={sheet.id}>
                  {sheet.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Choose an existing spreadsheet to use as a template
            </p>
          </div>

          {/* Project Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <div className="relative">
              <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                name="project_name"
                value={formData.project_name}
                onChange={handleInputChange}
                placeholder="e.g., NEST, ABC Project"
                className="input-field pl-10"
                required
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Enter the name of your project
            </p>
          </div>

          {/* Month */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Month
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                name="month"
                value={formData.month}
                onChange={handleInputChange}
                className="input-field pl-10"
                required
              >
                <option value="">Select month</option>
                {months.map((month) => (
                  <option key={month} value={month}>
                    {month}
                  </option>
                ))}
              </select>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Select the month for the new spreadsheet
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn-secondary"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 btn-primary flex items-center justify-center gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Create Spreadsheet
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateSpreadsheetModal;
