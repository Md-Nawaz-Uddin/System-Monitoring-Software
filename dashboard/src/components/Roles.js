import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Roles() {
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ username: '', password: '', features: [] });
  const [showForm, setShowForm] = useState(false);
  const featuresList = [
    'Inventory', 'Extensions', 'Software', 'System Actions', 'Audit Logs', 'Compliance & Reports',
    'Create Users', 'Delete Users'
  ];

  useEffect(() => {
    // Fetch users from backend (placeholder for now)
    const mockUsers = [
      {
        username: 'admin',
        features: featuresList,
        created_at: '2025-07-17T10:00:00Z'
      },
      {
        username: 'readonly_user',
        features: [],
        created_at: '2025-07-17T11:00:00Z'
      }
    ];
    setUsers(mockUsers);
  }, []);

  const handleCheckboxChange = (feature) => {
    setNewUser(prev => {
      const features = prev.features.includes(feature)
        ? prev.features.filter(f => f !== feature)
        : [...prev.features, feature];
      return { ...prev, features };
    });
  };

  const handleAddUser = () => {
    if (!newUser.username || newUser.password.length < 8) {
      alert("Please enter a valid username and password (min 8 characters).");
      return;
    }
    // Submit to backend (placeholder)
    console.log("Creating user:", newUser);
    alert("User created (mock).");
    setShowForm(false);
    setNewUser({ username: '', password: '', features: [] });
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">User Roles & Permissions</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow"
        >
          {showForm ? 'Cancel' : 'Add User'}
        </button>
      </div>

      {/* User Table */}
      <div className="overflow-x-auto bg-white shadow rounded mb-6">
        <table className="min-w-full table-auto">
          <thead className="bg-gray-200 text-gray-700">
            <tr>
              <th className="px-4 py-2 text-left">Username</th>
              <th className="px-4 py-2 text-left">Permissions</th>
              <th className="px-4 py-2 text-left">Created</th>
              <th className="px-4 py-2 text-left">Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-800">{user.username}</td>
                <td className="px-4 py-2 text-gray-800">{user.features.join(', ') || 'Read Only'}</td>
                <td className="px-4 py-2 text-gray-800">{new Date(user.created_at).toLocaleString()}</td>
                <td className="px-4 py-2 text-gray-800">
                  {user.features.includes('Create Users') || user.features.includes('Delete Users') ? 'Admin' : (user.features.length > 0 ? 'Custom' : 'Read Only')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {users.length === 0 && (
          <p className="p-4 text-gray-500 text-center">
            No users found.
          </p>
        )}
      </div>

      {showForm && (
        <div className="bg-white shadow rounded p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Create New User</h3>
          <div className="mb-4">
            <label className="block mb-1 text-gray-700">Username</label>
            <input
              type="text"
              value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              className="w-full border rounded px-3 py-2 text-black"
            />
          </div>
          <div className="mb-4">
            <label className="block mb-1 text-gray-700">Password</label>
            <input
              type="password"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              className="w-full border rounded px-3 py-2 text-black"
            />
            {newUser.password.length > 0 && newUser.password.length < 8 && (
              <p className="text-sm text-red-500 mt-1">Password must be at least 8 characters</p>
            )}
          </div>

          <div className="mb-4">
            <label className="block mb-2 text-gray-700 font-semibold">Feature Access</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {featuresList.map((feature, idx) => (
                <label key={idx} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="form-checkbox text-blue-600"
                    checked={newUser.features.includes(feature)}
                    onChange={() => handleCheckboxChange(feature)}
                  />
                  <span className="ml-2 text-gray-800">{feature}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={handleAddUser}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow"
          >
            Create User
          </button>
        </div>
      )}
    </div>
  );
}
