import React, { useState } from 'react';
import { X, FileText, Calendar, Building, Loader2 } from 'lucide-react';
import { spreadsheetAPI } from '../api';
import Modal from './ui/Modal';
import Button from './ui/Button';
import Input from './ui/Input';
import { Card, CardContent } from './ui/Card';

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
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Create New Spreadsheet"
      size="md"
      className="max-h-[90vh] overflow-y-auto"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Source Spreadsheet */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Spreadsheet
          </label>
          <select
            name="source_spreadsheet_id"
            value={formData.source_spreadsheet_id}
            onChange={handleInputChange}
            className="input w-full"
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
        <Input
          label="Project Name"
          type="text"
          name="project_name"
          value={formData.project_name}
          onChange={handleInputChange}
          placeholder="e.g., NEST, ABC Project"
          leftIcon={<Building className="w-4 h-4" />}
          helperText="Enter the name of your project"
          required
          disabled={isLoading}
        />

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
              className="input pl-10 w-full"
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
          <div className="bg-error-50 border border-error-200 rounded-lg p-4 animate-slide-up">
            <p className="text-sm text-error-800 font-medium">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            onClick={onClose}
            variant="secondary"
            size="md"
            className="flex-1"
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="md"
            loading={isLoading}
            className="flex-1"
            disabled={isLoading}
          >
            <FileText className="w-4 h-4" />
            Create Spreadsheet
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateSpreadsheetModal;
