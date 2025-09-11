import React, { useState, useEffect } from 'react';
import { LogOut, Plus, FileText, MessageSquare, BarChart3, Key, Menu, X } from 'lucide-react';
import { authAPI, documentsAPI } from '../api';
import Navigation from '../components/Navigation';
import ChatInterface from '../components/ChatInterface';
import CreateSpreadsheetModal from '../components/CreateSpreadsheetModal';
import ApiKeyModal from '../components/ApiKeyModal';
import AppLayout from '../components/layout/AppLayout';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [availableSheets, setAvailableSheets] = useState(null); // null indicates loading
  const [selectedSheet, setSelectedSheet] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [loading, setLoading] = useState(true);

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

        // Get available documents
        const documentsResponse = await documentsAPI.getDocuments();
        const documents = Array.isArray(documentsResponse.data) ? documentsResponse.data : [];
        setAvailableSheets(documents);
        
        // Select first sheet by default
        if (documents.length > 0) {
          setSelectedSheet(documents[0]);
        }

        // Check if user has Groq API key, if not show modal
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

  const handleSheetSelect = (sheet) => {
    setSelectedSheet(sheet);
  };

  const handleCreateSpreadsheet = async (projectName = null, useCurrentMonth = false) => {
    if (projectName) {
      // Direct creation for specific project
      await createSpreadsheetForProject(projectName, useCurrentMonth);
    } else {
      // Show modal for general creation
      setShowCreateModal(true);
    }
  };

  const createSpreadsheetForProject = async (projectName, useCurrentMonth = false) => {
    try {
      // Get current date and calculate month (next month or current month)
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
      
      // Find a DPR spreadsheet to use as template
      const dprSheets = availableSheets?.filter(sheet => 
        sheet.name.startsWith('DPR_')
      ) || [];
      
      if (dprSheets.length === 0) {
        alert('No DPR spreadsheets found to use as template. Please create one first.');
        return;
      }
      
      // Use the first DPR sheet as template
      const templateSheet = dprSheets[0];
      
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
      
      // Refresh the documents list
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
    } catch (error) {
      console.error('Error refreshing documents:', error);
    }
    setShowCreateModal(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading your workspace..." />
      </div>
    );
  }

  // Header component for the layout
  const header = (
    <div className="flex items-center justify-between w-full">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-sm">
          <FileText className="w-6 h-6 text-primary-600" />
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
      
      <div className="flex items-center gap-2">
        <Button
          onClick={handleManageApiKey}
          variant="ghost"
          size="sm"
          className="hidden sm:flex items-center gap-2"
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

  // Main content
  const mainContent = selectedSheet ? (
    <ChatInterface
      selectedSheet={selectedSheet}
      user={user}
    />
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
          onClick={handleCreateSpreadsheet}
          variant="primary"
          size="lg"
          className="w-full sm:w-auto"
        >
          <Plus className="w-5 h-5" />
          Create New Spreadsheet
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <AppLayout header={header} sidebar={sidebar}>
        {mainContent}
      </AppLayout>

      {/* Create Spreadsheet Modal */}
      {showCreateModal && (
        <CreateSpreadsheetModal
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
