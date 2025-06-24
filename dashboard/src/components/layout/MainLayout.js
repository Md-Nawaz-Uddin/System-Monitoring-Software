// src/components/layout/MainLayout.js
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function MainLayout({ onLogout }) {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="flex min-h-screen bg-lightbg text-sidebarText">
      {/* Sidebar */}
      <Sidebar onLogout={onLogout} />

      {/* Main content area */}
      <div className="flex-1 p-6">
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

        {/* Pass searchQuery to child routes like /devices */}
        <Outlet context={{ searchQuery }} />
      </div>
    </div>
  );
}
