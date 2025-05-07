import React, { useState } from 'react';

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  return (
    <header className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo and Title */}
          <div className="flex items-center">
            <span className="text-2xl font-bold">XTC</span>
            <span className="ml-2 text-blue-200">Task Manager</span>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-6">
            <a href="/" className="hover:text-blue-200 transition-colors">
              Dashboard
            </a>
            <a href="/tasks" className="hover:text-blue-200 transition-colors">
              Tasks
            </a>
            <a href="/projects" className="hover:text-blue-200 transition-colors">
              Projects
            </a>
            <a href="/settings" className="hover:text-blue-200 transition-colors">
              Settings
            </a>
          </nav>
          
          {/* Mobile Menu Button */}
          <button 
            className="md:hidden p-2 rounded-md hover:bg-blue-700 focus:outline-none"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-6 w-6" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d={isMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} 
              />
            </svg>
          </button>
        </div>
        
        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="md:hidden pt-4 pb-2 space-y-2">
            <a 
              href="/" 
              className="block py-2 px-2 hover:bg-blue-700 rounded transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Dashboard
            </a>
            <a 
              href="/tasks" 
              className="block py-2 px-2 hover:bg-blue-700 rounded transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Tasks
            </a>
            <a 
              href="/projects" 
              className="block py-2 px-2 hover:bg-blue-700 rounded transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Projects
            </a>
            <a 
              href="/settings" 
              className="block py-2 px-2 hover:bg-blue-700 rounded transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Settings
            </a>
          </nav>
        )}
      </div>
    </header>
  );
}

export default Header;
