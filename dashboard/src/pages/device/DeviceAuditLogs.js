// src/pages/devices/DeviceAuditLog.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

export default function DeviceAuditLog() {
  const { deviceId } = useParams();
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await axios.get(`/api/audit-logs?device_id=${deviceId}`);
        setLogs(res.data);
      } catch (err) {
        console.error("Failed to fetch audit logs:", err);
      }
    };

    fetchLogs();
  }, [deviceId]);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        Audit Logs for <span className="text-blue-600">{deviceId}</span>
      </h2>

      <div className="overflow-x-auto bg-white shadow rounded">
        <table className="min-w-full table-auto">
          <thead className="bg-gray-200 text-gray-700">
            <tr>
              <th className="px-4 py-2 text-left">Time</th>
              <th className="px-4 py-2 text-left">User</th>
              <th className="px-4 py-2 text-left">Action</th>
              <th className="px-4 py-2 text-left">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="px-4 py-2 text-gray-800">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-4 py-2 text-gray-800">{log.user}</td>
                <td className="px-4 py-2 text-gray-800">{log.action}</td>
                <td className="px-4 py-2 text-gray-800">
                  {log.details ? log.details : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {logs.length === 0 && (
          <p className="p-4 text-gray-500 text-center">
            No logs found for this device.
          </p>
        )}
      </div>
    </div>
  );
}
