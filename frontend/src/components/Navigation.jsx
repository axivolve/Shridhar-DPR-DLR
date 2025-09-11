import React, { useState, useMemo } from 'react';
import { FileText, Plus, Calendar, Users, ChevronDown, ChevronRight, Building, X } from 'lucide-react';
import Button from './ui/Button';
import { Card, CardContent } from './ui/Card';
import LoadingSpinner from './ui/LoadingSpinner';
import Skeleton from './ui/Skeleton';
import Input from './ui/Input';

const Navigation = ({ sheets = [], selectedSheet, onSheetSelect, onCreateSpreadsheet }) => {
  const [expandedDropdowns, setExpandedDropdowns] = useState({});
  const [loadingProjects, setLoadingProjects] = useState({});
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [showAddProjectModal, setShowAddProjectModal] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [error, setError] = useState('');

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

  const generateSpreadsheetName = (projectName) => {
    // Replace spaces with hyphens in project name and convert to uppercase
    const sanitizedProjectName = projectName.replace(/\s+/g, '-').toUpperCase();
    
    return sanitizedProjectName;
  };

  const parseSheetName = (name) => {
    // Check if sheet starts with DPR_
    if (!name.startsWith('DPR_')) {
      return null;
    }

    // Remove DPR_ prefix
    const withoutPrefix = name.substring(4);
    
    // Split by underscore to get parts
    const parts = withoutPrefix.split('_');
    
    if (parts.length < 2) {
      return null;
    }

    // Last two parts should be month and year
    const year = parts[parts.length - 1];
    const month = parts[parts.length - 2];
    
    // Everything before the last two parts is the project name
    const projectName = parts.slice(0, -2).join(' ').replace(/-/g, ' ');

    // Convert month name to proper format
    const monthNames = {
      'JANUARY': 'January',
      'FEBRUARY': 'February', 
      'MARCH': 'March',
      'APRIL': 'April',
      'MAY': 'May',
      'JUNE': 'June',
      'JULY': 'July',
      'AUGUST': 'August',
      'SEPTEMBER': 'September',
      'OCTOBER': 'October',
      'NOVEMBER': 'November',
      'DECEMBER': 'December'
    };

    const formattedMonth = monthNames[month.toUpperCase()] || month;
    const displayName = `${formattedMonth} ${year}`;

    return {
      projectName,
      month,
      year,
      displayName,
      originalName: name
    };
  };

  const organizedSheets = useMemo(() => {
    if (!Array.isArray(sheets)) return {};

    const organized = {};
    
    sheets.forEach(sheet => {
      const parsed = parseSheetName(sheet.name);
      if (parsed) {
        if (!organized[parsed.projectName]) {
          organized[parsed.projectName] = [];
        }
        organized[parsed.projectName].push({
          ...sheet,
          parsed
        });
      }
    });

    // Sort each project's sheets by year and month
    Object.keys(organized).forEach(projectName => {
      organized[projectName].sort((a, b) => {
        const monthOrder = {
          'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
          'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
          'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
        };
        
        const yearA = parseInt(a.parsed.year);
        const yearB = parseInt(b.parsed.year);
        
        if (yearA !== yearB) {
          return yearA - yearB;
        }
        
        return monthOrder[a.parsed.month.toUpperCase()] - monthOrder[b.parsed.month.toUpperCase()];
      });
    });

    return organized;
  }, [sheets]);

  const toggleDropdown = (projectName) => {
    setExpandedDropdowns(prev => ({
      ...prev,
      [projectName]: !prev[projectName]
    }));
  };

  const handleCreateSpreadsheet = async (projectName) => {
    // Set loading state for this project
    setLoadingProjects(prev => ({
      ...prev,
      [projectName]: true
    }));

    try {
      // Call the parent's create function
      await onCreateSpreadsheet(projectName);
    } catch (error) {
      console.error('Error creating spreadsheet:', error);
    } finally {
      // Clear loading state after a delay to show the animation
      setTimeout(() => {
        setLoadingProjects(prev => ({
          ...prev,
          [projectName]: false
        }));
      }, 2000); // Show loading for 2 seconds
    }
  };

  const handleAddProject = () => {
    setShowAddProjectModal(true);
    setProjectName('');
    setError('');
  };

  const handleProjectSubmit = async (e) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      setError('Project name is required');
      return;
    }

    const trimmedProjectName = projectName.trim();
    
    setIsCreatingProject(true);
    setError('');
    
    try {
      // Call the parent's create function with the project name and useCurrentMonth = true
      await onCreateSpreadsheet(trimmedProjectName, true);
      
      // Close modal and reset form
      setShowAddProjectModal(false);
      setProjectName('');
    } catch (error) {
      console.error('Error creating project:', error);
      setError('Failed to create project. Please try again.');
    } finally {
      setIsCreatingProject(false);
    }
  };

  const handleModalClose = () => {
    if (!isCreatingProject) {
      setShowAddProjectModal(false);
      setProjectName('');
      setError('');
    }
  };

  const totalSheets = Object.values(organizedSheets).reduce((total, projectSheets) => total + projectSheets.length, 0);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <Button
          onClick={handleAddProject}
          variant="primary"
          size="md"
          className="w-full justify-center gap-2"
          loading={isCreatingProject}
          disabled={isCreatingProject}
        >
          <Plus className="w-4 h-4" />
          {isCreatingProject ? 'Creating Project...' : 'Add Project'}
        </Button>
      </div>

      {/* Sheets List */}
      <div className="flex-1 overflow-y-auto scrollbar-hide">
        {!Array.isArray(sheets) ? (
          <div className="p-6">
            <LoadingSpinner size="md" text="Loading spreadsheets..." />
          </div>
        ) : Object.keys(organizedSheets).length === 0 ? (
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Projects Yet
            </h3>
            <p className="text-gray-600 text-sm mb-4 text-balance">
              Create your first project to start managing DPR and DLR reports
            </p>
            <Button
              onClick={() => onCreateSpreadsheet()}
              variant="outline"
              size="sm"
              className="w-full"
            >
              <Plus className="w-4 h-4" />
              Create First Project
            </Button>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {Object.entries(organizedSheets).map(([projectName, projectSheets]) => (
              <Card key={projectName} className="border-0 shadow-none bg-transparent">
                <CardContent className="p-0">
                  {/* Project Dropdown Header */}
                  <div className="flex items-center justify-between p-3 rounded-lg transition-colors duration-200 hover:bg-gray-50 border border-transparent">
                    <div 
                      onClick={() => toggleDropdown(projectName)}
                      className="flex items-center gap-3 cursor-pointer flex-1 touch-target"
                    >
                      {expandedDropdowns[projectName] ? (
                        <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-gray-500 flex-shrink-0" />
                      )}
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <Building className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <h3 className="font-medium text-sm text-gray-900 truncate">{projectName}</h3>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full flex-shrink-0">
                          {projectSheets.length}
                        </span>
                      </div>
                    </div>
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCreateSpreadsheet(projectName);
                      }}
                      variant="ghost"
                      size="sm"
                      className="w-8 h-8 p-0"
                      disabled={loadingProjects[projectName]}
                    >
                      {loadingProjects[projectName] ? (
                        <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Plus className="w-4 h-4" />
                      )}
                    </Button>
                  </div>

                  {/* Project Sheets */}
                  {expandedDropdowns[projectName] && (
                    <div className="ml-6 mt-1 space-y-1 animate-slide-up">
                      {projectSheets.map((sheet) => (
                        <div
                          key={sheet.id}
                          onClick={() => onSheetSelect(sheet)}
                          className={`p-3 rounded-lg cursor-pointer transition-all duration-200 touch-target ${
                            selectedSheet?.id === sheet.id
                              ? 'bg-primary-50 border border-primary-200 shadow-sm'
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
                              <h4 className={`font-medium text-sm truncate ${
                                selectedSheet?.id === sheet.id
                                  ? 'text-primary-900'
                                  : 'text-gray-900'
                              }`}>
                                {sheet.parsed.displayName}
                              </h4>
                              
                              <div className="flex items-center gap-2 mt-1">
                                <Calendar className="w-3 h-3 text-gray-400" />
                                <span className="text-xs text-gray-500">
                                  {formatDate(sheet.modifiedTime)}
                                </span>
                              </div>
                              
                              {sheet.owners && sheet.owners.length > 0 && (
                                <div className="flex items-center gap-1 mt-1">
                                  <Users className="w-3 h-3 text-gray-400" />
                                  <span className="text-xs text-gray-500 truncate">
                                    {sheet.owners[0].displayName || sheet.owners[0].emailAddress}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {/* Loading Animation */}
                      {loadingProjects[projectName] && (
                        <div className="p-3 rounded-lg bg-gray-50 border border-gray-200 animate-pulse">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                              <div className="w-4 h-4 border-2 border-gray-300 border-t-primary-600 rounded-full animate-spin" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium text-sm text-gray-600">
                                Creating new DPR DLR sheet...
                              </h4>
                              <p className="text-xs text-gray-500 mt-1">
                                Please wait while we prepare your new month
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="text-xs text-gray-500 text-center space-y-1">
          <p className="font-medium">
            {totalSheets} DPR spreadsheet{totalSheets !== 1 ? 's' : ''}
          </p>
          <p>
            {Object.keys(organizedSheets).length} project{Object.keys(organizedSheets).length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Add Project Modal */}
      {showAddProjectModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <Card className="max-w-md w-full animate-slide-up">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Plus className="w-5 h-5 text-primary-600" />
                </div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Add New Project
                </h2>
              </div>
              <Button
                onClick={handleModalClose}
                variant="ghost"
                size="sm"
                className="w-8 h-8 p-0"
                disabled={isCreatingProject}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {/* Form */}
            <form onSubmit={handleProjectSubmit} className="p-6 space-y-6">
              <Input
                label="Project Name"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g., Olive Gardens, Office Complex"
                leftIcon={<Building className="w-4 h-4" />}
                helperText="Enter the name of your new project"
                required
                disabled={isCreatingProject}
                error={error}
              />

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  onClick={handleModalClose}
                  variant="secondary"
                  size="md"
                  className="flex-1"
                  disabled={isCreatingProject}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  loading={isCreatingProject}
                  className="flex-1"
                  disabled={isCreatingProject || !projectName.trim()}
                >
                  <Plus className="w-4 h-4" />
                  Create Project
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

    </div>
  );
};

export default Navigation;
