import React, { useState } from 'react';
import { FileText, AlertCircle, ArrowLeft } from 'lucide-react';
import AuthForm from '../components/AuthForm';
import { authAPI } from '../api';
import Button from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import Container from '../components/layout/Container';

const Login = () => {
  const [authStep, setAuthStep] = useState('auth'); // 'auth', 'google'
  const [error, setError] = useState('');
  const [userData, setUserData] = useState(null);

  const handleAuthSuccess = (data) => {
    setUserData(data);
    
    // After successful authentication, proceed directly to Google login
    setAuthStep('google');
  };

  const handleGoogleLogin = () => {
    authAPI.googleLogin();
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

  const clearError = () => {
    setError('');
  };

  const handleBackToAuth = () => {
    setAuthStep('auth');
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 safe-top safe-bottom">
      <Container size="sm" className="min-h-screen flex flex-col justify-center py-8">
        <div className="w-full">
          {/* Logo/Header */}
          <div className="text-center mb-8 animate-in">
            <div className="mx-auto w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mb-6 shadow-lg">
              <FileText className="w-10 h-10 text-primary-600" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3 text-balance">
              AI Works Tracker
            </h1>
            <p className="text-gray-600 text-base sm:text-lg text-balance max-w-md mx-auto">
              Manage your Daily Progress Reports and Daily Log Reports with AI-powered insights
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 animate-slide-up">
              <Card className="border-error-200 bg-error-50">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-error-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm text-error-800 font-medium">{error}</p>
                      <button
                        onClick={clearError}
                        className="text-xs text-error-600 hover:text-error-500 mt-2 font-medium"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Auth Steps */}
          {authStep === 'auth' && (
            <div className="animate-in">
              <AuthForm onSuccess={handleAuthSuccess} onError={handleError} />
            </div>
          )}

          {authStep === 'google' && (
            <Card className="animate-slide-up">
              <CardContent className="p-6 sm:p-8 text-center">
                <div className="mb-6">
                  <div className="mx-auto w-20 h-20 bg-success-100 rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                    <svg className="w-10 h-10 text-success-600" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-3">
                    Connect Google Account
                  </h2>
                  <p className="text-gray-600 text-balance">
                    Now connect your Google account to access Google Sheets and start managing your AI Works Tracker reports.
                  </p>
                </div>

                <div className="space-y-4">
                  <Button
                    onClick={handleGoogleLogin}
                    variant="outline"
                    size="lg"
                    className="w-full justify-center gap-3 h-14 text-base"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24">
                      <path
                        fill="#4285F4"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="#34A853"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="#FBBC05"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="#EA4335"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    Continue with Google
                  </Button>

                  <Button
                    onClick={handleBackToAuth}
                    variant="ghost"
                    size="md"
                    className="w-full"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Sign In
                  </Button>
                </div>

                <div className="mt-6 text-sm text-gray-500 text-balance">
                  By continuing, you agree to our terms of service and privacy policy
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </Container>
    </div>
  );
};

export default Login;
