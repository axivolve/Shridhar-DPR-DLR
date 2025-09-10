# DPR-DLR Management Frontend

A modern React frontend application for managing Daily Progress Reports (DPR) and Daily Log Reports (DLR) with AI-powered analysis and Google Sheets integration.

## 🚀 Features

- **Google OAuth2 Authentication**: Secure login with Google accounts
- **AI-Powered Chat Interface**: Natural language processing for DPR/DLR updates
- **Three Operation Modes**:
  - **DPR Updates**: Daily Progress Report management
  - **DLR Updates**: Daily Log Report management with fuzzy matching
  - **Log Analysis**: AI-powered insights and analysis
- **Spreadsheet Management**: Create new monthly spreadsheets automatically
- **Real-time Updates**: Live chat interface with instant feedback
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **React 18** with Vite for fast development
- **Tailwind CSS** for modern, responsive styling
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for beautiful icons
- **Date-fns** for date manipulation

## 📦 Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and navigate to `http://localhost:5173`

## 🔧 Configuration

The frontend is configured to connect to the backend running on `http://localhost:8000`. If your backend is running on a different port or host, update the `baseURL` in `src/api/index.js`:

```javascript
const apiClient = axios.create({
  baseURL: 'http://your-backend-url:port',
  // ... other config
});
```

## 📁 Project Structure

```
src/
├── api/                    # API service layer
│   └── index.js           # Centralized API client with JWT management
├── components/            # Reusable UI components
│   ├── ProtectedRoute.jsx # Route protection component
│   ├── Navigation.jsx     # Sidebar navigation
│   ├── ChatInterface.jsx  # Main chat interface
│   └── CreateSpreadsheetModal.jsx # Modal for creating new spreadsheets
├── pages/                 # Page components
│   ├── Login.jsx         # Google OAuth login page
│   ├── AuthCallback.jsx  # OAuth callback handler
│   └── Dashboard.jsx     # Main dashboard
├── App.jsx               # Main app component with routing
├── main.jsx              # Application entry point
└── index.css             # Global styles with Tailwind
```

## 🔐 Authentication Flow

1. **Login**: Users click "Sign in with Google" and are redirected to Google OAuth
2. **Callback**: After successful authentication, users are redirected back with a JWT token
3. **Token Storage**: The JWT token is stored in localStorage for API requests
4. **Protected Routes**: All main app routes require authentication
5. **Auto-logout**: Token expiration automatically redirects to login

## 💬 Chat Interface

The chat interface supports three modes:

### DPR Mode
- **Purpose**: Update Daily Progress Reports
- **Example**: "Completed foundation work for Block A, 50% progress"
- **Backend**: Calls `/update-dpr/{sheet_id}` endpoint

### DLR Mode
- **Purpose**: Update Daily Log Reports with fuzzy matching
- **Example**: "Added 10 cubic meters of concrete to Block B"
- **Backend**: Calls `/update-dlr/{sheet_id}` endpoint

### Logs Mode
- **Purpose**: Analyze and query log data
- **Example**: "What was the total concrete used this month?"
- **Backend**: Calls `/analyze-logs/{sheet_id}` endpoint

## 📊 Spreadsheet Management

- **View All Sheets**: Browse all accessible Google Sheets in the sidebar
- **Create New Spreadsheet**: Automatically create monthly spreadsheets with:
  - Source template selection
  - Project name configuration
  - Month selection
  - Automatic date population
  - Previous month data transfer

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface with Tailwind CSS
- **Responsive Layout**: Two-column layout that adapts to screen size
- **Loading States**: Smooth loading indicators for all operations
- **Error Handling**: User-friendly error messages and recovery
- **Real-time Feedback**: Instant visual feedback for all user actions

## 🔄 API Integration

The frontend integrates with the following backend endpoints:

- `GET /user/me` - Get current user information
- `GET /documents` - List all accessible Google Sheets
- `POST /update-dpr/{sheet_id}` - Update DPR data
- `POST /update-dlr/{sheet_id}` - Update DLR data
- `POST /analyze-logs/{sheet_id}` - Analyze log data
- `POST /new-spreadsheet` - Create new spreadsheet

## 🚀 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

Create a `.env` file in the frontend directory if needed:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

The layout automatically adapts to different screen sizes with:
- Collapsible sidebar on mobile
- Touch-friendly interface elements
- Optimized chat interface for small screens

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your backend has CORS enabled for the frontend URL
2. **Authentication Issues**: Check that JWT tokens are being stored correctly
3. **API Connection**: Verify the backend is running on the correct port
4. **Build Errors**: Clear node_modules and reinstall dependencies

### Debug Mode

Enable debug logging by opening browser developer tools and checking the console for detailed error messages.

## 📄 License

This project is part of the DPR-DLR Management System.