import React, { useState } from 'react';
import { Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';
import MobileDrawer from '../mobile/MobileDrawer';

const AppLayout = ({
  children,
  sidebar,
  header,
  className = '',
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDesktopSidebarCollapsed, setIsDesktopSidebarCollapsed] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const toggleDesktopSidebar = () => {
    setIsDesktopSidebarCollapsed(!isDesktopSidebarCollapsed);
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Mobile Header */}
      <header className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 safe-top">
        <div className="flex items-center justify-between">
          <button
            onClick={toggleMobileMenu}
            className="touch-target text-gray-600 hover:text-gray-900"
            aria-label="Open menu"
          >
            <Menu className="w-6 h-6" />
          </button>
          {header}
        </div>
      </header>

      {/* Desktop Header */}
      <header className="hidden lg:block bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleDesktopSidebar}
              className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
              aria-label={isDesktopSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {isDesktopSidebarCollapsed ? (
                <ChevronRight className="w-5 h-5" />
              ) : (
                <ChevronLeft className="w-5 h-5" />
              )}
            </button>
            {header}
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-64px)] lg:h-[calc(100vh-80px)]">
        {/* Mobile Sidebar Drawer */}
        <MobileDrawer
          isOpen={isMobileMenuOpen}
          onClose={() => setIsMobileMenuOpen(false)}
          title="Projects"
          position="left"
          size="md"
        >
          {sidebar}
        </MobileDrawer>

        {/* Desktop Sidebar */}
        <aside className={`hidden lg:block bg-white border-r border-gray-200 overflow-y-auto transition-all duration-300 ease-in-out ${
          isDesktopSidebarCollapsed ? 'w-16' : 'w-80'
        }`}>
          <div className={`transition-all duration-300 ease-in-out delay-75 ${
            isDesktopSidebarCollapsed ? 'opacity-0 scale-95 pointer-events-none' : 'opacity-100 scale-100 pointer-events-auto'
          }`}>
            {sidebar}
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
