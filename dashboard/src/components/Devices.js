import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Devices() {
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    axios.get('/api/devices').then(res => {
      setDevices(res.data);
    });
  }, []);

  return (
    <div>
      <h3>Devices</h3>
      <table>
        <thead><tr><th>Hostname</th><th>CPU</th><th>RAM</th><th>Disk</th></tr></thead>
        <tbody>
          {devices.map((d, idx) => (
            <tr key={idx}>
              <td>{d.hostname}</td><td>{d.cpu}</td><td>{d.ram}</td><td>{d.disk}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export default Devices;

