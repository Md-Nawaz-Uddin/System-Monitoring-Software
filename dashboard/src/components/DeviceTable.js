import React, { useEffect, useState } from 'react';
import axios from 'axios';

function DeviceTable() {
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    axios.get('/api/devices').then(res => {
      setDevices(res.data);
    });
  }, []);

  return (
    <table>
      <thead>
        <tr>
          <th>Hostname</th><th>CPU</th><th>RAM</th><th>Disk</th><th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {devices.map((d, idx) => (
          <tr key={idx}>
            <td>{d.hostname}</td>
            <td>{d.cpu}</td>
            <td>{d.ram}</td>
            <td>{d.disk}</td>
            <td>{d.timestamp}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DeviceTable;
