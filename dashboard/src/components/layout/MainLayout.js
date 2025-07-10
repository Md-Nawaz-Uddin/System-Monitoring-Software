// src/components/layout/MainLayout.js
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function MainLayout({ onLogout }) {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="flex bg-lightbg text-sidebarText">
      {/* Sticky Sidebar */}
      <div className="fixed top-0 left-0 h-screen w-64 z-10">
        <Sidebar onLogout={onLogout} />
      </div>

      {/* Main content area with left margin to avoid overlapping */}
      <div className="ml-64 flex-1 p-6 min-h-screen overflow-y-auto">
        {/* Top search bar */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search devices..."
            className="w-full max-w-md px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-blue-400 text-gray-800"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Pass searchQuery to child routes */}
        <Outlet context={{ searchQuery }} />
      </div>
    </div>
  );
}
