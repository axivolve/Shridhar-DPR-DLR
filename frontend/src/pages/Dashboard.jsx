import React, { useState, useEffect } from 'react';
import { LogOut, Plus, FileText, MessageSquare, BarChart3, Key, Menu, X, Upload, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';
import { authAPI, documentsAPI, workspaceAPI } from '../api';
import Navigation from '../components/Navigation';
import ChatInterface from '../components/ChatInterface';
import NewProjectModal from '../components/NewProjectModal';
import ApiKeyModal from '../components/ApiKeyModal';
import AppLayout from '../components/layout/AppLayout';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Logo from '../components/ui/Logo';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [availableSheets, setAvailableSheets] = useState(null); // null indicates loading
  const [selectedSheet, setSelectedSheet] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [initializing, setInitializing] = useState(false);
  const [initializationStatus, setInitializationStatus] = useState(null);
  const [loadingStep, setLoadingStep] = useState('Loading your workspace...');

  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        // Get user info from localStorage (simple auth)
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          setUser({
            name: userData.name || userData.username,
            email: userData.email,
            phone_number: userData.phone_number
          });
        } else {
          // Fallback to API call if no stored user
          const userResponse = await authAPI.getCurrentUser();
          setUser(userResponse.data);
        }

        // Initialize workspace (check and upload DPR_FORMAT if needed)
        setLoadingStep('Initializing workspace...');
        setInitializing(true);
        try {
          setLoadingStep('Checking for DPR_FORMAT...');
          const initResponse = await workspaceAPI.initializeWorkspace();
          setInitializationStatus(initResponse.data);
          
          if (initResponse.data.success) {
            console.log('Workspace initialized:', initResponse.data);
            if (initResponse.data.action_taken === 'uploaded') {
              setLoadingStep('DPR_FORMAT uploaded successfully');
            } else if (initResponse.data.action_taken === 'found') {
              setLoadingStep('DPR_FORMAT found - almost ready!');
            } else {
              setLoadingStep('Workspace ready!');
            }
          } else {
            console.error('Workspace initialization failed:', initResponse.data.error);
            setLoadingStep('Workspace setup failed');
          }
        } catch (initError) {
          console.error('Error initializing workspace:', initError);
          setInitializationStatus({
            success: false,
            error: 'Failed to initialize workspace'
          });
          setLoadingStep('Workspace setup failed');
        } finally {
          setInitializing(false);
        }

        // Get available documents
        setLoadingStep('Loading your spreadsheets...');
        const documentsResponse = await documentsAPI.getDocuments();
        const documents = Array.isArray(documentsResponse.data) ? documentsResponse.data : [];
        setAvailableSheets(documents);
        
        // Filter out template sheets and select first valid project sheet
        const validProjectSheets = documents.filter(sheet => {
          // Only include sheets that start with DPR_ and follow the project naming convention
          if (!sheet.name.startsWith('DPR_')) return false;
          
          // Exclude template sheets like DPR_FORMAT
          if (sheet.name === 'DPR_FORMAT') return false;
          
          // Check if it follows the project naming pattern: DPR_PROJECTNAME_MONTH_YEAR
          const withoutPrefix = sheet.name.substring(4);
          const parts = withoutPrefix.split('_');
          return parts.length >= 3; // At least project name, month, and year
        });
        
        // Select the latest valid project sheet by default
        if (validProjectSheets.length > 0) {
          // Sort by creation date (assuming newer sheets have higher IDs or we can sort by name)
          const sortedSheets = validProjectSheets.sort((a, b) => {
            // Sort by name to get the most recent month/year combination
            return b.name.localeCompare(a.name);
          });
          setSelectedSheet(sortedSheets[0]);
        }

        // Check if user has Groq API key, if not show modal
        setLoadingStep('Finalizing setup...');
        const groqApiKey = localStorage.getItem('groq_api_key');
        if (!groqApiKey) {
          setShowApiKeyModal(true);
        }
      } catch (error) {
        console.error('Error initializing dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeDashboard();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user');
    localStorage.removeItem('groq_api_key');
    window.location.href = '/login';
  };

  const handleApiKeySave = (apiKey) => {
    console.log('Groq API key saved:', apiKey ? 'Yes' : 'No');
    setShowApiKeyModal(false);
  };

  const handleApiKeyModalClose = () => {
    setShowApiKeyModal(false);
  };

  const handleManageApiKey = () => {
    setShowApiKeyModal(true);
  };

  const handleOpenSpreadsheet = () => {
    if (selectedSheet?.webViewLink) {
      window.open(selectedSheet.webViewLink, '_blank');
    }
  };

  const handleSheetSelect = (sheet) => {
    setSelectedSheet(sheet);
  };

  const handleCreateSpreadsheet = async (projectName = null, useCurrentMonth = true) => {
    if (projectName) {
      // Direct creation for specific project
      await createSpreadsheetForProject(projectName, useCurrentMonth);
    } else {
      // Show modal for general creation
      setShowCreateModal(true);
    }
  };

  const handleOpenCreateModal = () => {
    setShowCreateModal(true);
  };

  const createSpreadsheetForProject = async (projectName, useCurrentMonth = true) => {
    try {
      // Get current date and calculate month (current month or next month)
      const now = new Date();
      const targetMonth = useCurrentMonth 
        ? new Date(now.getFullYear(), now.getMonth(), 1)
        : new Date(now.getFullYear(), now.getMonth() + 1, 1);
      
      const monthNames = [
        'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
        'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'
      ];
      
      const monthName = monthNames[targetMonth.getMonth()];
      const year = targetMonth.getFullYear();
      
      // Log the date calculation for debugging
      console.log('Date calculation details:', {
        useCurrentMonth,
        now: now.toISOString(),
        targetMonth: targetMonth.toISOString(),
        monthName,
        year,
        monthIndex: targetMonth.getMonth()
      });
      
      // Find DPR_FORMAT sheet to use as template
      const dprFormatSheet = availableSheets?.find(sheet => 
        sheet.name === 'DPR_FORMAT'
      );
      
      if (!dprFormatSheet) {
        alert('DPR_FORMAT template sheet not found. Please ensure your workspace is properly initialized.');
        return;
      }
      
      // Use DPR_FORMAT as template
      const templateSheet = dprFormatSheet;
      
      // Create the new spreadsheet name in DPR format
      const newSpreadsheetName = `DPR_${projectName.replace(/\s+/g, '-').toUpperCase()}_${monthName}_${year}`;
      
      // Prepare request data
      const requestData = {
        spreadsheet_id: templateSheet.id,
        project_name: projectName.replace(/\s+/g, '-').toUpperCase(), // Convert spaces to dashes and uppercase
        month: monthName
      };
      
      console.log('Creating DPR spreadsheet with data:', requestData);
      
      // Call the API
      const response = await fetch('http://localhost:8000/new-spreadsheet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: JSON.stringify(requestData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create spreadsheet');
      }
      
      const result = await response.json();
      console.log('Spreadsheet created successfully:', result);
      
      // Refresh the documents list and select the new sheet
      await handleSpreadsheetCreated();
      
    } catch (error) {
      console.error('Error creating spreadsheet:', error);
      alert(`Failed to create spreadsheet: ${error.message}`);
    }
  };


  const handleModalClose = () => {
    setShowCreateModal(false);
  };

  const handleSpreadsheetCreated = async () => {
    // Refresh the documents list
    try {
      const documentsResponse = await documentsAPI.getDocuments();
      const documents = Array.isArray(documentsResponse.data) ? documentsResponse.data : [];
      setAvailableSheets(documents);
      
      // Filter and select the latest valid project sheet
      const validProjectSheets = documents.filter(sheet => {
        if (!sheet.name.startsWith('DPR_')) return false;
        if (sheet.name === 'DPR_FORMAT') return false;
        const withoutPrefix = sheet.name.substring(4);
        const parts = withoutPrefix.split('_');
        return parts.length >= 3;
      });
      
      if (validProjectSheets.length > 0) {
        const sortedSheets = validProjectSheets.sort((a, b) => {
          return b.name.localeCompare(a.name);
        });
        setSelectedSheet(sortedSheets[0]);
      }
    } catch (error) {
      console.error('Error refreshing documents:', error);
    }
    setShowCreateModal(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" text={loadingStep} />
          {initializationStatus && !initializationStatus.success && (
            <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200 max-w-md">
              <div className="flex items-center justify-center gap-2 text-red-700">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Setup Error</span>
              </div>
              <p className="text-xs text-red-600 mt-1">
                {initializationStatus.error || 'Unknown error occurred'}
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Header components for the layout
  const headerLeft = (
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm border border-gray-200">
        <Logo size="md" />
      </div>
      <div className="hidden sm:block">
        <h1 className="text-xl font-semibold text-gray-900">AI Works Tracker</h1>
        <p className="text-sm text-gray-600">
          Welcome back, {user?.name || 'User'}
        </p>
      </div>
      <div className="sm:hidden">
        <h1 className="text-lg font-semibold text-gray-900">AI Works Tracker</h1>
      </div>
    </div>
  );

  const headerRight = (
    <div className="flex items-center gap-2">
      <Button
        onClick={handleOpenSpreadsheet}
        variant="ghost"
        size="sm"
        className="flex items-center gap-2"
        disabled={!selectedSheet?.webViewLink}
        title={selectedSheet?.webViewLink ? "Open in Google Sheets" : "No spreadsheet selected"}
      >
        <ExternalLink className="w-4 h-4" />
        <span className="hidden lg:inline">Open Sheet</span>
      </Button>
      
      <Button
        onClick={handleManageApiKey}
        variant="ghost"
        size="sm"
        className="flex items-center gap-2"
      >
        <Key className="w-4 h-4" />
        <span className="hidden lg:inline">API Key</span>
      </Button>
      
      <Button
        onClick={handleLogout}
        variant="ghost"
        size="sm"
        className="flex items-center gap-2"
      >
        <LogOut className="w-4 h-4" />
        <span className="hidden lg:inline">Logout</span>
      </Button>
    </div>
  );

  // For mobile, combine both parts
  const header = (
    <div className="flex items-center justify-between w-full">
      {headerLeft}
      {headerRight}
    </div>
  );

  // Sidebar component for the layout
  const sidebar = (
    <Navigation
      sheets={availableSheets}
      selectedSheet={selectedSheet}
      onSheetSelect={handleSheetSelect}
      onCreateSpreadsheet={handleCreateSpreadsheet}
    />
  );

  // Check if there are any valid project sheets
  const validProjectSheets = availableSheets?.filter(sheet => {
    if (!sheet.name.startsWith('DPR_')) return false;
    if (sheet.name === 'DPR_FORMAT') return false;
    const withoutPrefix = sheet.name.substring(4);
    const parts = withoutPrefix.split('_');
    return parts.length >= 3;
  }) || [];

  // Main content
  const mainContent = selectedSheet ? (
    <ChatInterface
      selectedSheet={selectedSheet}
      user={user}
    />
  ) : validProjectSheets.length === 0 ? (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <MessageSquare className="w-10 h-10 text-gray-400" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-3">
          No Projects Found
        </h3>
        <p className="text-gray-600 mb-6 text-balance">
          Create your first project to start managing DPR and DLR reports. Projects help organize your construction data by month and year.
        </p>
        <Button
          onClick={handleOpenCreateModal}
          variant="primary"
          size="lg"
          className="w-full sm:w-auto"
        >
          <Plus className="w-5 h-5" />
          Create Your First Project
        </Button>
      </div>
    </div>
  ) : (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <MessageSquare className="w-10 h-10 text-gray-400" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-3">
          No Spreadsheet Selected
        </h3>
        <p className="text-gray-600 mb-6 text-balance">
          Choose a spreadsheet from the sidebar to start managing your DPR and DLR data, or create a new one.
        </p>
        <Button
          onClick={handleOpenCreateModal}
          variant="primary"
          size="lg"
          className="w-full sm:w-auto"
        >
          <Plus className="w-5 h-5" />
          Create New Project
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <AppLayout 
        header={header} 
        headerLeft={headerLeft}
        headerRight={headerRight}
        sidebar={sidebar}
      >
        {mainContent}
      </AppLayout>

      {/* New Project Modal */}
      {showCreateModal && (
        <NewProjectModal
          availableSheets={availableSheets || []}
          onClose={handleModalClose}
          onSuccess={handleSpreadsheetCreated}
        />
      )}

      {/* API Key Modal */}
      {showApiKeyModal && (
        <ApiKeyModal
          isOpen={showApiKeyModal}
          onClose={handleApiKeyModalClose}
          onSave={handleApiKeySave}
        />
      )}
    </>
  );
};

export default Dashboard;
