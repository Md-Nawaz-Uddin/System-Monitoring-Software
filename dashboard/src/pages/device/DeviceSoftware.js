import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

export default function DeviceSoftware() {
  const { deviceId } = useParams();
  const [softwareList, setSoftwareList] = useState([]);
  const [services, setServices] = useState([]);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    axios.get(`/api/devices/${deviceId}/software`)
      .then(res => setSoftwareList(res.data))
      .catch(err => console.error(err));

    axios.get(`/api/devices/${deviceId}/services`)
      .then(res => setServices(res.data))
      .catch(err => console.error(err));
  }, [deviceId]);

  const uninstallSoftware = (name) => {
    axios.delete(`/api/devices/${deviceId}/software/${encodeURIComponent(name)}`)
      .then(() => setSoftwareList(prev => prev.filter(soft => soft.name !== name)))
      .catch(err => console.error(err));
  };

  const killProcess = (name) => {
    axios.post(`/api/devices/${deviceId}/processes/${encodeURIComponent(name)}/kill`)
      .then(() => {
        alert(`${name} has been marked for termination.`);
        axios.get(`/api/devices/${deviceId}/software`)
          .then(res => setSoftwareList(res.data));
      })
      .catch(err => console.error(err));
  };

  const handleServiceAction = (action, name) => {
    const url = action === 'delete'
      ? `/api/devices/${deviceId}/services/${name}/delete`
      : `/api/devices/${deviceId}/services/${name}/${action}`;

    axios.post(url)
      .then(() => {
        alert(`${action.charAt(0).toUpperCase() + action.slice(1)} queued. It will be applied during next agent run.`);
        axios.get(`/api/devices/${deviceId}/services`)
          .then(res => setServices(res.data));
      })
      .catch(err => console.error(err));
  };

  const filtered = useMemo(() => {
    if (filter === 'running-services') {
      return services.filter(s => s.name.toLowerCase().includes(search.toLowerCase()));
    }
    return softwareList.filter(s => {
      if (filter === 'running' && s.state !== 'running') return false;
      if (filter === 'installed' && s.state !== 'installed') return false;
      if (search && !s.name.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [filter, search, softwareList, services]);

  const stateColor = {
    running: 'bg-green-100 text-green-800',
    installed: 'bg-gray-100 text-gray-800'
  };

  return (
    <div className="text-gray-800">
      <div className="flex justify-between items-center mb-6">
        <input
          type="text"
          placeholder="Search software/services..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="px-4 py-2 border rounded-lg w-full max-w-sm text-sm shadow-sm"
        />
        <div className="space-x-2 ml-4">
          {[
            { key: 'all', label: 'All' },
            { key: 'running', label: 'Running Processes' },
            { key: 'installed', label: 'Current Softwares' },
            { key: 'running-services', label: 'Running Services' }
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className={`px-4 py-2 rounded-lg text-sm capitalize transition-colors duration-200 ${
                filter === key ? 'bg-indigo-600 text-white' : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-gray-500">No matching software or service found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filter === 'running-services'
            ? filtered.map((s, i) => (
              <div key={i} className="p-4 border rounded-xl shadow-sm bg-white hover:shadow-md transition-all">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold text-gray-900 text-base">{s.name}</h4>
                    <p className="text-sm text-gray-500 mb-1">Description: {s.description || 'N/A'}</p>
                    <p className="text-sm text-gray-500">Status: <span className="text-green-600">{s.status}</span>, Startup: <span className="text-blue-600">{s.startup}</span></p>
                    <p className="text-sm text-gray-500">CPU: <strong>{s.cpu}</strong> | RAM: <strong>{s.ram}</strong></p>
                  </div>
                  <div className="flex flex-col space-y-2">
                    {s.status === 'running' ? (
                      <button onClick={() => handleServiceAction('stop', s.name)} className="px-3 py-1 bg-yellow-400 text-white rounded-lg hover:bg-yellow-500 text-sm shadow">
                        Stop
                      </button>
                    ) : (
                      <button onClick={() => handleServiceAction('start', s.name)} className="px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm shadow">
                        Start
                      </button>
                    )}
                    <button onClick={() => handleServiceAction('restart', s.name)} className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm shadow">
                      Restart
                    </button>
                    <button onClick={() => handleServiceAction('disable', s.name)} className="px-3 py-1 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm shadow">
                      Disable
                    </button>
                    <button onClick={() => handleServiceAction('delete', s.name)} className="px-3 py-1 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm shadow">
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
            : filtered.map((s, i) => (
              <div key={i} className="p-4 border rounded-xl shadow-sm bg-white hover:shadow-md transition-all">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-semibold text-gray-900 text-base">{s.name}</h4>
                    <p className="text-sm text-gray-500 mb-1">Version: {s.version || 'N/A'}</p>
                    <p className="text-sm text-gray-500">Path: {s.path || 'N/A'}</p>
                    <p className="text-sm text-gray-500">Type: {s.type || 'N/A'}</p>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${stateColor[s.state] || 'bg-gray-100 text-gray-700'}`}>{s.state}</span>
                    {s.state === 'running' && s.type === 'process' ? (
                      <button onClick={() => killProcess(s.name)} className="px-3 py-1 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 shadow">
                        Kill
                      </button>
                    ) : (
                      <button onClick={() => uninstallSoftware(s.name)} className="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 shadow">
                        Uninstall
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}
