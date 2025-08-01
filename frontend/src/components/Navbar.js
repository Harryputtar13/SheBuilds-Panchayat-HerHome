import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mic, Menu, X, Home, FileText, Users, Settings } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Home', href: '/', icon: <Home className="w-5 h-5" /> },
    { name: 'Survey', href: '/survey', icon: <FileText className="w-5 h-5" /> },
    { name: 'Results', href: '/results', icon: <Users className="w-5 h-5" /> },
    { name: 'Admin', href: '/admin', icon: <Settings className="w-5 h-5" /> },
  ];

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <img 
              src="/logo.jpeg" 
              alt="Her Home Logo" 
              className="w-12 h-12 rounded-lg object-cover"
            />
            <div>
              <span className="text-xl font-bold text-pink-600">Her Home</span>
              <div className="text-xs text-gray-500">Find Your Perfect Roommate</div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === item.href
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            ))}
            
            {/* Her Home Status */}
            <div className="flex items-center space-x-2 px-3 py-2 bg-pink-50 text-pink-700 rounded-md">
              <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
              <span className="text-sm font-medium">AI Ready</span>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-700 hover:text-blue-600 focus:outline-none focus:text-blue-600"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="md:hidden bg-white border-t border-gray-200"
        >
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setIsOpen(false)}
                className={`flex items-center space-x-3 px-3 py-2 rounded-md text-base font-medium transition-colors ${
                  location.pathname === item.href
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            ))}
            
            {/* Mobile Her Home Status */}
            <div className="flex items-center space-x-3 px-3 py-2 bg-pink-50 text-pink-700 rounded-md">
              <div className="w-2 h-2 bg-pink-500 rounded-full"></div>
              <span className="text-base font-medium">Her Home AI Ready</span>
            </div>
          </div>
        </motion.div>
      )}
    </nav>
  );
};

export default Navbar; 