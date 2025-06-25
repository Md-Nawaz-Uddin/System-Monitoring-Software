import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

export default function DeviceSoftware() {
  const { deviceId } = useParams();
  const [softwareList, setSoftwareList] = useState([]);
  const [services, setServices] = useState([]);
  const [filter, setFilter] = useState('all'); // all | running | installed | running-services
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
      .then(() => {
        setSoftwareList(prev => prev.filter(soft => soft.name !== name));
      })
      .catch(err => console.error(err));
  };

const handleServiceAction = (action, name) => {
  const url = action === 'delete'
    ? `/api/devices/${deviceId}/services/${name}/delete`
    : `/api/devices/${deviceId}/services/${name}/${action}`;

  axios.post(url)
    .then(() => {
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
      <div className="flex justify-between items-center mb-4">
        <input
          type="text"
          placeholder="Search software/services..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="px-3 py-2 border rounded w-full max-w-sm text-sm"
        />
        <div className="space-x-2 ml-4">
        {['all', 'running', 'installed', 'running-services'].map(state => (
  <button
    key={state}
    onClick={() => setFilter(state)}
    className={`px-3 py-1 rounded text-sm capitalize ${
      filter === state ? 'bg-blue-600 text-white' : 'bg-gray-200'
    }`}
  >
    {state === 'running' ? 'running processes' : state.replace('-', ' ')}
  </button>
))}

      </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-gray-500">No matching software or service found.</p>
      ) : (
        <div className="space-y-4">
          {filter === 'running-services' ? (
            filtered.map((s, i) => (
              <div key={i} className="p-4 border rounded shadow bg-white">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-gray-800">{s.name}</h4>
                    <p className="text-sm text-gray-500">Description: {s.description || 'N/A'}</p>
                    <p className="text-sm text-gray-500">Status: {s.status}, Startup: {s.startup}</p>
                    <p className="text-sm text-gray-500">CPU: {s.cpu || '0%'} | RAM: {s.ram || '0 MB'}</p>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    {s.status === 'running' ? (
                      <button
                        onClick={() => handleServiceAction('stop', s.name)}
                        className="px-3 py-1 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600"
                      >
                        Stop
                      </button>
                    ) : (
                      <button
                        onClick={() => handleServiceAction('start', s.name)}
                        className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                      >
                        Start
                      </button>
                    )}
                    <button
                      onClick={() => handleServiceAction('restart', s.name)}
                      className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Restart
                    </button>
                    <button
                      onClick={() => handleServiceAction('disable', s.name)}
                      className="px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                      Disable
                    </button>
                    <button
                      onClick={() => handleServiceAction('delete', s.name)}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            filtered.map((s, i) => (
              <div key={i} className="p-4 border rounded shadow bg-white">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-gray-800">{s.name}</h4>
                    <p className="text-sm text-gray-500">Version: {s.version || 'N/A'}</p>
                    <p className="text-sm text-gray-500">Path: {s.path || 'N/A'}</p>
                    <p className="text-sm text-gray-500">Type: {s.type || 'N/A'}</p>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span className={`text-xs px-2 py-1 rounded ${stateColor[s.state] || 'bg-gray-100 text-gray-700'}`}>
                      {s.state}
                    </span>
                    <button
                      onClick={() => uninstallSoftware(s.name)}
                      className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Uninstall
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
