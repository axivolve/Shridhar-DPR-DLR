import React, { useState, useEffect } from 'react';
import { Building, Plus, Calendar } from 'lucide-react';
import { spreadsheetAPI } from '../api';
import Modal from './ui/Modal';
import Button from './ui/Button';
import Input from './ui/Input';

const NewProjectModal = ({ availableSheets, onClose, onSuccess }) => {
  // Find DPR_FORMAT sheet and set it as default
  const dprFormatSheet = availableSheets?.find(sheet => sheet.name === 'DPR_FORMAT');
  
  const [formData, setFormData] = useState({
    source_spreadsheet_id: dprFormatSheet?.id || '',
    project_name: '',
    month: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const months = [
    'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
    'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'
  ];

  // Auto-set current month and year
  useEffect(() => {
    const now = new Date();
    const currentMonth = months[now.getMonth()];
    const currentYear = now.getFullYear();
    
    setFormData(prev => ({
      ...prev,
      month: currentMonth,
      source_spreadsheet_id: dprFormatSheet?.id || ''
    }));
  }, [dprFormatSheet]);

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
    
    if (!formData.project_name.trim()) {
      setError('Please enter a project name');
      return;
    }

    if (!formData.source_spreadsheet_id) {
      setError('DPR_FORMAT template not found. Please ensure the template is available.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Map the form data to match backend expectations
      const requestData = {
        spreadsheet_id: formData.source_spreadsheet_id,
        project_name: formData.project_name.trim(),
        month: formData.month.toUpperCase() // Backend expects uppercase month names
      };
      
      console.log('Creating new project with data:', requestData);
      await spreadsheetAPI.createNewSpreadsheet(requestData);
      onSuccess();
    } catch (error) {
      console.error('Error creating project:', error);
      console.error('Error details:', error.response?.data);
      
      // Handle different error response formats
      let errorMessage = 'Failed to create project';
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
      title="Create New Project"
      size="lg"
      className="max-h-[90vh] overflow-y-auto"
    >
      <div className="px-1">
        {/* Header Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <Plus className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Start a New Project</h2>
          <p className="text-sm text-gray-600">
            Create a new project with DPR DLR sheet ready for{' '}
            <span className="inline-flex items-center gap-1 font-medium text-blue-600">
              <Calendar className="w-4 h-4" />
              {formData.month} {new Date().getFullYear()}
            </span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Project Name Input */}
          <div className="space-y-2">
            <Input
              label="Project Name"
              type="text"
              name="project_name"
              value={formData.project_name}
              onChange={handleInputChange}
              placeholder="Enter your project name"
              leftIcon={<Building className="w-4 h-4" />}
              helperText="Choose a descriptive name for your project"
              required
              disabled={isLoading}
              className="text-base"
            />
          </div>

          {/* Hidden fields for automatic values */}
          <input type="hidden" name="source_spreadsheet_id" value={formData.source_spreadsheet_id} />
          <input type="hidden" name="month" value={formData.month} />

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 animate-slide-up">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-800 font-medium">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-6 border-t border-gray-200">
            <Button
              type="button"
              onClick={onClose}
              variant="secondary"
              size="lg"
              className="flex-1"
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              className="flex-1"
              disabled={isLoading}
            >
              Create Project
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default NewProjectModal;
