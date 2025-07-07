// src/pages/devices/DeviceActions.js

import React from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

export default function DeviceActions() {
  const { deviceId } = useParams();

  const performAction = async (action) => {
    try {
      const endpoint =
        action === 'patch'
          ? `/api/devices/${deviceId}/actions/patch-system`
          : `/api/devices/${deviceId}/action/${action}`;

      console.log("🔧 Sending action to:", endpoint);
      await axios.post(endpoint);

      alert(`✅ ${action.charAt(0).toUpperCase() + action.slice(1)} sent successfully!`);
    } catch (error) {
      console.error(`❌ Failed to send ${action} command:`, error);
      alert(`❌ ${action} failed`);
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">
        System Actions for <span className="text-blue-600">{deviceId}</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ActionButton
          label="Shutdown"
          color="bg-red-600"
          icon="⏻"
          buttonText="Shutdown Now"
          onClick={() => performAction('shutdown')}
        />
        <ActionButton
          label="Restart"
          color="bg-yellow-500"
          icon="🔄"
          buttonText="Restart Now"
          onClick={() => performAction('restart')}
        />
        <ActionButton
          label="Lock User"
          color="bg-blue-600"
          icon="🔒"
          buttonText="Lock Now"
          onClick={() => performAction('lock')}
        />
        <ActionButton
          label="Unlock User"
          color="bg-blue-400"
          icon="🔓"
          buttonText="Unlock Now"
          onClick={() => performAction('unlock')}
        />
        <ActionButton
          label="Remote Access"
          color="bg-purple-600"
          icon="🖥️"
          buttonText="Request Access"
          onClick={() => performAction('remote')}
        />
        <ActionButton
          label="Enable USB (Temp)"
          color="bg-green-600"
          icon="🔌"
          buttonText="Enable Temporarily"
          onClick={() => performAction('enable-usb')}
        />
        <ActionButton
          label="Patch System"
          color="bg-indigo-600"
          icon="🛠️"
          buttonText="Apply Patch"
          onClick={() => performAction('patch')}
        />
      </div>
    </div>
  );
}

function ActionButton({ label, icon, color, buttonText, onClick }) {
  return (
    <div className={`rounded-lg shadow-md p-6 flex flex-col items-center justify-center ${color} text-white`}>
      <div className="text-4xl mb-2">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{label}</h3>
      <button
        onClick={onClick}
        className="mt-2 px-4 py-2 bg-white text-black font-medium rounded hover:bg-gray-200 transition"
      >
        {buttonText}
      </button>
    </div>
  );
}
