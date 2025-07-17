// src/pages/Dashboard.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Dashboard() {
  const [deviceStats, setDeviceStats] = useState({});
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchStats();
    fetchLogs();

    const interval = setInterval(fetchLogs, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const res = await axios.get('/api/dashboard/stats');
      setDeviceStats(res.data);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get('/api/audit-logs');
      setLogs(res.data.slice(0, 10)); // latest 10
    } catch (err) {
      console.error("Failed to fetch logs:", err);
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard Overview</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <StatCard title="Total Devices" value={deviceStats.totalDevices || 0} color="bg-blue-600" />
        <StatCard title="Devices Online" value={deviceStats.online || 0} color="bg-green-600" />
        <StatCard title="Devices Offline" value={deviceStats.offline || 0} color="bg-red-600" />
      </div>

      {/* System Activity Logs */}
      <div className="bg-white rounded shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent System Activity</h2>
        <div className="max-h-64 overflow-y-auto text-sm">
          {logs.length === 0 ? (
            <p className="text-gray-500">No recent logs.</p>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className="border-b py-2">
                <span className="text-gray-500 mr-2">{new Date(log.timestamp).toLocaleString()}</span>
                <span className="text-gray-800 font-medium">{log.user}</span> performed <span className="text-indigo-600">{log.action}</span> on <span className="text-gray-700">{log.device}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Patch Status / Compliance */}
      <div className="bg-white rounded shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Patch & Compliance Summary</h2>
        <p className="text-sm text-gray-600">
          {deviceStats.compliantDevices || 0} out of {deviceStats.totalDevices || 0} devices are compliant with patch policies.
        </p>
      </div>
    </div>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div className={`rounded-lg shadow-md p-6 text-white ${color}`}>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}
