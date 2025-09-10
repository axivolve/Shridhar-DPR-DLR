import React, { useState, useEffect } from 'react';
import { LogOut, Plus, FileText, MessageSquare, BarChart3, Key } from 'lucide-react';
import { authAPI, documentsAPI } from '../api';
import Navigation from '../components/Navigation';
import ChatInterface from '../components/ChatInterface';
import CreateSpreadsheetModal from '../components/CreateSpreadsheetModal';
import ApiKeyModal from '../components/ApiKeyModal';

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
        // Get user info
        const userResponse = await authAPI.getCurrentUser();
        setUser(userResponse.data);

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

  const handleCreateSpreadsheet = () => {
    setShowCreateModal(true);
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
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">DPR-DLR Management</h1>
              <p className="text-sm text-gray-600">
                Welcome back, {user?.name || 'User'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* <button
              onClick={handleCreateSpreadsheet}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Spreadsheet
            </button> */}
            
            <button
              onClick={handleManageApiKey}
              className="btn-secondary flex items-center gap-2"
            >
              <Key className="w-4 h-4" />
              API Key
            </button>
            
            <button
              onClick={handleLogout}
              className="btn-secondary flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Sidebar - Navigation */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <Navigation
            sheets={availableSheets}
            selectedSheet={selectedSheet}
            onSheetSelect={handleSheetSelect}
            onCreateSpreadsheet={handleCreateSpreadsheet}
          />
        </div>

        {/* Right Main Area - Chat Interface */}
        <div className="flex-1 flex flex-col">
          {selectedSheet ? (
            <ChatInterface
              selectedSheet={selectedSheet}
              user={user}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Spreadsheet Selected
                </h3>
                <p className="text-gray-600 mb-4">
                  Choose a spreadsheet from the sidebar to start managing your DPR and DLR data.
                </p>
                <button
                  onClick={handleCreateSpreadsheet}
                  className="btn-primary flex items-center gap-2 mx-auto"
                >
                  <Plus className="w-4 h-4" />
                  Create New Spreadsheet
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

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
    </div>
  );
};

export default Dashboard;
