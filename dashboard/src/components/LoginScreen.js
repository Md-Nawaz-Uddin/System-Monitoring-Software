import React, { useState } from 'react';

export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    onLogin(username, password, setError);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-600 to-indigo-700">
      <div className="bg-white rounded-lg shadow-lg flex flex-col md:flex-row w-full max-w-4xl overflow-hidden">
        
        {/* Left Branding/Image Section */}
        <div
          className="md:w-1/2 p-8 flex flex-col justify-center items-center text-center"
          style={{
            backgroundImage: `url('/MoniAlac-login-page-bg.png')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div className="bg-white/70 p-6 rounded-lg">
            <h1 className="text-3xl font-bold text-gray-800">MoniAlac</h1>
            <p className="text-gray-700 text-sm mt-2">
              Endpoint Monitoring & Extension Control Dashboard
            </p>
          </div>
        </div>

        {/* Right Form Section */}
        <div className="md:w-1/2 p-8 bg-white">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800 text-center">Login to Continue</h2>

          <input
            className="w-full px-4 py-2 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            className="w-full px-4 py-2 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <div className="text-red-500 text-sm mb-2">{error}</div>}

          <button
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
            onClick={handleSubmit}
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
}
