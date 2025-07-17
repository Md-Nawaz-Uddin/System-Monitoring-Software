// src/pages/DeviceDetail.js
import { useParams, NavLink, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function DeviceDetail() {
  const { deviceId } = useParams();
  const [device, setDevice] = useState(null);

  useEffect(() => {
    axios.get(`/api/devices/${deviceId}`)
      .then(res => setDevice(res.data))
      .catch(err => console.error('Device fetch failed', err));
  }, [deviceId]);

  if (!device) {
    return <div className="p-6 text-gray-600">Loading device info...</div>;
  }

  return (
    <div className="p-6 text-gray-800">
      <h2 className="text-2xl font-semibold mb-2">{device.name}</h2>
      <p className="text-sm mb-4 text-gray-600">
        IP: {device.ip} | OS: {device.os} | Status: {device.status}
      </p>

      <nav className="flex space-x-4 border-b border-gray-300 mb-4">
        {['inventory', 'extensions', 'software', 'actions', 'logs', 'compliance'].map(tab => (
          <NavLink
            key={tab}
            to={`/devices/${deviceId}/${tab}`}
            className={({ isActive }) =>
              `px-4 py-2 text-sm font-medium ${
                isActive
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`
            }
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </NavLink>
        ))}
      </nav>

      <Outlet />
    </div>
  );
}
