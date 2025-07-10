// src/components/Sidebar.js
import { NavLink } from 'react-router-dom';
import { Home, Search, Settings, Users, Clock, LogOut } from 'lucide-react';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: <Home size={18} /> },
  { to: '/devices', label: 'Devices', icon: <Search size={18} /> },
  { to: '/settings', label: 'Settings', icon: <Settings size={18} /> },
  { to: '/roles', label: 'Roles', icon: <Users size={18} /> },
  { to: '/recent', label: 'Recent Activity', icon: <Clock size={18} /> }
];

export default function Sidebar({ onLogout }) {
  return (
    <div className="fixed top-0 left-0 h-screen w-64 bg-primary text-sidebarText flex flex-col justify-between z-50">
      <div>
        <div className="text-center p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold">🛡️ MonAlac</h1>
        </div>

        <nav className="p-4 space-y-1 overflow-y-auto">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center px-4 py-2 rounded transition ${
                  isActive ? 'bg-secondary' : 'hover:bg-secondary'
                }`
              }
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={onLogout}
          className="flex items-center w-full px-4 py-2 rounded text-sidebarText hover:bg-secondary transition"
        >
          <LogOut size={18} className="mr-3" />
          Logout
        </button>
      </div>
    </div>
  );
}
