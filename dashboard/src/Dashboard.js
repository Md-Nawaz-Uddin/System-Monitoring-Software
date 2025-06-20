import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);         // 👈 NEW
  const [error, setError] = useState(null);             // 👈 NEW

  useEffect(() => {
    axios.get('/api/devices', { withCredentials: true })
      .then(res => {
        setDevices(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError('Unauthorized or session expired');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-6 text-gray-700">Loading...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;   // 👈 Show error only if exists

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-4">📊 System Dashboard</h1>

      <table className="min-w-full bg-white rounded shadow">
        <thead>
          <tr className="bg-gray-200 text-left">
            <th className="p-2">Hostname</th>
            <th className="p-2">OS</th>
            <th className="p-2">CPU</th>
            <th className="p-2">RAM</th>
            <th className="p-2">Disk</th>
            <th className="p-2">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {devices.map((d, i) => (
            <tr key={i} className="border-t">
              <td className="p-2">{d.hostname}</td>
              <td className="p-2">{d.os}</td>
              <td className="p-2">{d.cpu}%</td>
              <td className="p-2">{d.ram} GB</td>
              <td className="p-2">{d.disk} GB</td>
              <td className="p-2">{new Date(d.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Dashboard;

