// src/pages/Devices.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [filteredDevices, setFilteredDevices] = useState([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('/api/devices')
      .then(res => {
        setDevices(res.data);
        setFilteredDevices(res.data);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to fetch devices. Make sure you are logged in and the backend is running.');
      });
  }, []);

  useEffect(() => {
    const term = search.toLowerCase();
    const filtered = devices.filter(device =>
      device.hostname?.toLowerCase().includes(term) ||
      device.ip?.toLowerCase().includes(term) ||
      device.os?.toLowerCase().includes(term)
    );
    setFilteredDevices(filtered);
  }, [search, devices]);

  const handleActionSelect = (deviceId, feature) => {
    if (feature) navigate(`/devices/${deviceId}/${feature}`);
  };

  return (
    <div className="p-6 text-gray-800">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Devices</h2>
        <input
          type="text"
          placeholder="Search devices..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-blue-400 text-gray-800"
        />
      </div>

      {error && <p className="text-red-500">{error}</p>}

      {filteredDevices.length === 0 ? (
        <p className="text-gray-500">No matching devices found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredDevices.map((device) => (
            <div key={device.id} className="bg-white rounded-2xl shadow p-6 border border-gray-100 flex justify-between items-start hover:shadow-md transition">
              {/* Device Info */}
              <div>
                <h3 className="text-xl font-bold text-gray-900">{device.hostname}</h3>
                <p className="text-sm text-gray-600">IP: {device.ip}</p>
                <p className="text-sm text-gray-600">OS: {device.os}</p>
                <p className="text-sm">
                  Status:{' '}
                  <span className={device.status === 'online' ? 'text-green-600 font-medium' : 'text-red-500 font-medium'}>
                    {device.status}
                  </span>
                </p>
              </div>

              {/* Action Selector */}
              <div>
                <select
                  className="mt-1 text-sm border-gray-300 rounded-md text-gray-800 px-3 py-1 focus:outline-none focus:ring focus:ring-blue-300"
                  defaultValue=""
                  onChange={(e) => handleActionSelect(device.id, e.target.value)}
                >
                  <option value="" disabled>Select</option>
                  <option value="inventory">Inventory</option>
                  <option value="extensions">Extensions</option>
                  <option value="software">Software</option>
                  <option value="actions">System Actions</option>
                  <option value="logs">Audit Logs</option>
                  <option value="compliance">Compliance</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
