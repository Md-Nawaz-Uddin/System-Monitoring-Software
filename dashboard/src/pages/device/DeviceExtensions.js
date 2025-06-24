import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

export default function DeviceExtensions() {
  const { deviceId } = useParams();
  const [extensions, setExtensions] = useState([]);
  const [whitelist, setWhitelist] = useState({ vscode: [], browser: [] });
  const [blacklist, setBlacklist] = useState([]);
  const [activeTab, setActiveTab] = useState('whitelisted');
  const [newExtension, setNewExtension] = useState('');
  const [extensionType, setExtensionType] = useState('vscode');

  useEffect(() => {
    axios.get(`/api/devices/${deviceId}/extensions`).then(res => setExtensions(res.data));
    axios.get(`/api/devices/${deviceId}/extension-policy`).then(res => setWhitelist(res.data));
    axios.get(`/api/devices/${deviceId}/extension-blacklist`).then(res => {
      setBlacklist(res.data.vscode || []);
    });
  }, [deviceId]);

  const isWhitelisted = (ext) => {
    const list = whitelist[ext.type] || [];
    return list.map(name => name.toLowerCase()).includes(ext.name.toLowerCase());
  };

  const isBlacklisted = (ext) => {
    return blacklist.map(name => name.toLowerCase()).includes(ext.name.toLowerCase());
  };

  const addToWhitelist = () => {
    if (!newExtension.trim()) return;
    const updated = {
      ...whitelist,
      [extensionType]: [...(whitelist[extensionType] || []), newExtension.trim()]
    };
    updateWhitelist(updated);
    setNewExtension('');
  };

  const moveToNotWhitelisted = (name, type) => {
    const updated = {
      ...whitelist,
      [type]: whitelist[type].filter(ext => ext.toLowerCase() !== name.toLowerCase())
    };
    updateWhitelist(updated);
  };

  const moveToBlacklist = (name) => {
    const updated = [...blacklist, name];
    setBlacklist(updated);
    axios.post(`/api/devices/${deviceId}/extension-blacklist`, {
      vscode: updated
    });
  };

  const updateWhitelist = (newPolicy) => {
    axios.post(`/api/devices/${deviceId}/extension-policy`, newPolicy).then(() => {
      setWhitelist(newPolicy);
    });
  };

  const filteredExtensions = extensions.filter(ext => {
    if (activeTab === 'whitelisted') return isWhitelisted(ext);
    if (activeTab === 'blacklisted') return isBlacklisted(ext);
    return !isWhitelisted(ext) && !isBlacklisted(ext);
  });

  return (
    <div className="text-gray-800">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Add to Whitelist</h3>
        <div className="flex space-x-2 mb-2">
          <input
            type="text"
            value={newExtension}
            onChange={e => setNewExtension(e.target.value)}
            placeholder="Extension name..."
            className="w-full px-3 py-1 border border-gray-300 rounded text-sm"
          />
          <select
            value={extensionType}
            onChange={e => setExtensionType(e.target.value)}
            className="px-2 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="vscode">VS Code</option>
            <option value="browser">Browser</option>
          </select>
          <button
            onClick={addToWhitelist}
            className="px-4 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Add
          </button>
        </div>
      </div>

      <div className="flex space-x-4 mb-4">
        <button
          onClick={() => setActiveTab('whitelisted')}
          className={`px-4 py-2 rounded ${activeTab === 'whitelisted' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800'}`}
        >
          ✅ In Whitelist
        </button>
        <button
          onClick={() => setActiveTab('noncompliant')}
          className={`px-4 py-2 rounded ${activeTab === 'noncompliant' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-800'}`}
        >
          ❌ Not Whitelisted
        </button>
        <button
          onClick={() => setActiveTab('blacklisted')}
          className={`px-4 py-2 rounded ${activeTab === 'blacklisted' ? 'bg-black text-white' : 'bg-gray-200 text-gray-800'}`}
        >
          🛑 Blacklisted
        </button>
      </div>

      <ul className="space-y-4">
        {filteredExtensions.map((ext, index) => (
          <li
            key={index}
            className={`p-4 border rounded shadow ${
              isWhitelisted(ext)
                ? 'bg-green-50 border-green-200'
                : isBlacklisted(ext)
                ? 'bg-black text-white border-gray-800'
                : 'bg-red-50 border-red-200'
            }`}
          >
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-semibold">{ext.name}</h4>
                <p className="text-sm text-gray-400">Type: {ext.type}</p>
              </div>
              {isWhitelisted(ext) ? (
                <button
                  onClick={() => moveToNotWhitelisted(ext.name, ext.type)}
                  className="text-sm text-yellow-600 hover:underline"
                >
                  Move to Not Whitelisted
                </button>
              ) : isBlacklisted(ext) ? (
                <span className="text-sm text-white opacity-60">Auto removed</span>
              ) : (
                <button
                  onClick={() => moveToBlacklist(ext.name)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Blacklist
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
