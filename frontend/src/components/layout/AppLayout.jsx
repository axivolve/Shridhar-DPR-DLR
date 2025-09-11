import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import MobileDrawer from '../mobile/MobileDrawer';

const AppLayout = ({
  children,
  sidebar,
  header,
  className = '',
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
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
        {header}
      </header>

      <div className="flex h-[calc(100vh-64px)] lg:h-[calc(100vh-80px)]">
        {/* Mobile Sidebar Drawer */}
        <MobileDrawer
          isOpen={isMobileMenuOpen}
          onClose={() => setIsMobileMenuOpen(false)}
          title="Navigation"
          position="left"
          size="md"
        >
          {sidebar}
        </MobileDrawer>

        {/* Desktop Sidebar */}
        <aside className="hidden lg:block w-80 bg-white border-r border-gray-200 overflow-y-auto">
          {sidebar}
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
