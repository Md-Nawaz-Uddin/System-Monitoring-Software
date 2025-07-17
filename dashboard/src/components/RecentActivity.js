import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function RecentActivity() {
  const [logs, setLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await axios.get('/api/command-log');
      setLogs(res.data || []);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  };

  const filteredLogs = logs.filter(log =>
    [log.user, log.action, log.device, log.details]
      .join(' ')
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6">
      <h2 className="text-3xl font-bold mb-4 text-gray-800">Recent Activity (All Devices)</h2>

      {/* Search bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by user, action, device or details..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-blue-400 text-gray-800"
        />
      </div>

      {/* Log table */}
      <div className="overflow-x-auto bg-white shadow rounded">
        <table className="min-w-full table-auto">
          <thead className="bg-gray-200 text-gray-700">
            <tr>
              <th className="px-4 py-2 text-left">Time</th>
              <th className="px-4 py-2 text-left">User</th>
              <th className="px-4 py-2 text-left">Action</th>
              <th className="px-4 py-2 text-left">Device</th>
              <th className="px-4 py-2 text-left">Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map((log, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-800">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-4 py-2 text-gray-800">{log.user}</td>
                <td className="px-4 py-2 text-indigo-700 font-medium">{log.action}</td>
                <td className="px-4 py-2 text-gray-800">{log.device}</td>
                <td className="px-4 py-2 text-gray-800">{log.details || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredLogs.length === 0 && (
          <p className="p-4 text-gray-500 text-center">
            No logs found matching your search.
          </p>
        )}
      </div>
    </div>
  );
}
