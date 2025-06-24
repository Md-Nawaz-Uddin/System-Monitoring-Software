// src/pages/DeviceInventory.js
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

export default function DeviceInventory() {
  const { deviceId } = useParams();
  const [info, setInfo] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get(`/api/devices/${deviceId}/inventory`)
      .then(res => setInfo(res.data))
      .catch(err => {
        console.error(err);
        setError('Failed to load inventory.');
      });
  }, [deviceId]);

  const parseUsage = (usageStr) => {
    const [used, total] = usageStr.split('/').map(s => parseFloat(s));
    return (used / total) * 100;
  };

  const getColor = (percent) => {
    if (percent < 50) return 'bg-green-500';
    if (percent < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (error) return <p className="text-red-600">{error}</p>;
  if (!info) return <p className="text-gray-500">Loading...</p>;

  return (
    <div className="text-gray-800">
      <h3 className="text-xl font-semibold mb-4">System Details</h3>

      <ul className="mb-6 space-y-1 text-sm text-gray-600">
        <li><strong>Hostname:</strong> {info.hostname}</li>
        <li><strong>Model:</strong> {info.model}</li>
        <li><strong>Firmware:</strong> {info.firmware}</li>
        <li><strong>CPU:</strong> {info.cpu}</li>
        <li><strong>GPU:</strong> {info.gpu}</li>
        <li><strong>RAM:</strong> {info.ram}</li>
        <li><strong>Storage:</strong> {info.storage}</li>
        <li><strong>OS:</strong> {info.os}</li>
        <li><strong>GNOME:</strong> {info.gnome}</li>
        <li><strong>Windowing:</strong> {info.windowing}</li>
        <li><strong>Kernel:</strong> {info.kernel}</li>
	<li><strong>Last Updated:</strong> {info.last_updated}</li>
      </ul>

      <h4 className="text-lg font-medium mb-2">Resource Usage</h4>

      <div className="mb-4">
        <p className="text-sm mb-1">CPU Usage: {info.cpu_usage}</p>
        <div className="w-full h-3 bg-gray-200 rounded">
          <div
            className={`h-3 rounded ${getColor(parseFloat(info.cpu_usage))}`}
            style={{ width: info.cpu_usage }}
          ></div>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm mb-1">RAM Usage: {info.ram_usage}</p>
        <div className="w-full h-3 bg-gray-200 rounded">
          <div
            className={`h-3 rounded ${getColor(parseUsage(info.ram_usage))}`}
            style={{ width: `${parseUsage(info.ram_usage)}%` }}
          ></div>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm mb-1">Disk Usage: {info.disk_usage}</p>
        <div className="w-full h-3 bg-gray-200 rounded">
          <div
            className={`h-3 rounded ${getColor(parseUsage(info.disk_usage))}`}
            style={{ width: `${parseUsage(info.disk_usage)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
