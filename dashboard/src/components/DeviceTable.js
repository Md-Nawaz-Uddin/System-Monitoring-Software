import React, { useEffect, useState } from 'react';
import axios from 'axios';

function DeviceTable() {
  const [devices, setDevices] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('/api/devices')
      .then(res => setDevices(res.data))
      .catch(err => {
        console.error("Failed to fetch devices", err);
        setError("Could not load devices");
      });
  }, []);

  return (
    <div className="overflow-x-auto">
      <h3 className="text-lg font-semibold mb-3">🖥️ Monitored Devices</h3>
      
      {error && <div className="text-red-500 mb-2">{error}</div>}

      <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
        <thead className="bg-gray-100 text-gray-700 text-sm">
          <tr>
            <th className="px-4 py-2 text-left">Hostname</th>
            <th className="px-4 py-2 text-left">CPU (%)</th>
            <th className="px-4 py-2 text-left">RAM (%)</th>
            <th className="px-4 py-2 text-left">Disk (%)</th>
            <th className="px-4 py-2 text-left">Last Report</th>
          </tr>
        </thead>
        <tbody className="text-sm text-gray-800">
          {devices.length === 0 ? (
            <tr>
              <td colSpan="5" className="px-4 py-4 text-center text-gray-400">
                No data available
              </td>
            </tr>
          ) : (
            devices.map((d, idx) => (
              <tr key={idx} className="border-t hover:bg-gray-50">
                <td className="px-4 py-2">{d.hostname}</td>
                <td className="px-4 py-2">{d.cpu.toFixed(1)}%</td>
                <td className="px-4 py-2">{d.ram.toFixed(1)}%</td>
                <td className="px-4 py-2">{d.disk.toFixed(1)}%</td>
                <td className="px-4 py-2">{new Date(d.timestamp).toLocaleString()}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default DeviceTable;
