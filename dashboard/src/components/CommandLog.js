import React, { useEffect, useState } from 'react';
import axios from 'axios';

function CommandLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    axios.get('/api/command-log').then(res => {
      setLogs(res.data);
    });
  }, []);

  return (
    <div>
      <h3>Command Log</h3>
      <ul>
        {logs.map((log, idx) => (
          <li key={idx}>{log.time} — {log.user} ran {log.action} on {log.device}</li>
        ))}
      </ul>
    </div>
  );
}

export default CommandLog;
