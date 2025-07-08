import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

export default function DeviceActions() {
  const { deviceId } = useParams();
  const [showUsbModal, setShowUsbModal] = useState(false);
  const [duration, setDuration] = useState(10); // in minutes

  const performAction = async (action, data = {}) => {
  try {
    // Handle USB action by opening modal to choose duration
    if (action === 'enable-usb') {
      setShowUsbModal(true);  // Show modal and stop further execution
      return;
    }

    // Determine correct endpoint
    const endpoint =
      action === 'patch'
        ? `/api/devices/${deviceId}/actions/patch-system`
        : `/api/devices/${deviceId}/action/${action}`;

    console.log("🔧 Sending action to:", endpoint);
    await axios.post(endpoint, data);  // Include optional payload (like duration)

    alert(`✅ ${action.charAt(0).toUpperCase() + action.slice(1)} sent successfully!`);
  } catch (error) {
    console.error(`❌ Failed to send ${action} command:`, error);
    alert(`❌ ${action} failed`);
  }
};


  const submitUsbEnable = async () => {
    try {
      await axios.post(`/api/devices/${deviceId}/actions/enable-usb`, { duration });
      alert(`✅ USB enabled for ${duration} minutes`);
      setShowUsbModal(false);
    } catch (err) {
      console.error("❌ USB enable failed", err);
      alert("❌ Failed to enable USB");
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

      {/* USB Modal */}
      {showUsbModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Enable USB Temporarily</h3>

            <label className="block mb-2 text-gray-700">Select Duration</label>
            <select
  value={duration}
  onChange={(e) => setDuration(parseInt(e.target.value))}
  className="w-full px-4 py-2 border border-gray-300 rounded mb-4 bg-white text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
>
  <option value={5}>5 minutes</option>
  <option value={15}>15 minutes</option>
  <option value={30}>30 minutes</option>
  <option value={60}>1 hour</option>
  <option value={120}>2 hours</option>
  <option value={360}>6 hours</option>
  <option value={720}>12 hours</option>
  <option value={1440}>1 day</option>
</select>
     
            
	     <div className="flex justify-end space-x-4">
              <button
                className="px-4 py-2 bg-red-400 rounded hover:bg-red-500"
                onClick={() => setShowUsbModal(false)}
              >
                Cancel
              </button>
              <button
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                onClick={submitUsbEnable}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
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
