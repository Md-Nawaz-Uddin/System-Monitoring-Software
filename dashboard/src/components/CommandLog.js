import React, { useEffect, useState } from 'react';
import axios from 'axios';

function CommandLog() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get('/api/command-log')
      .then((res) => {
        setLogs(res.data);
      })
      .catch((err) => {
        console.error("Error fetching command logs:", err);
        setError("Failed to load logs");
      });
  }, []);

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-bold mb-4">🔧 Command Log</h2>

      {error && <div className="text-red-500 mb-2">{error}</div>}

      <ul className="space-y-2">
        {logs.length === 0 ? (
          <li className="text-gray-500">No logs available</li>
        ) : (
          logs.map((log, idx) => (
            <li key={idx} className="text-sm text-gray-700">
              🕒 {new Date(log.time).toLocaleString()} — <strong>{log.user}</strong> ran <code>{log.action}</code> on <em>{log.device}</em>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default CommandLog;
