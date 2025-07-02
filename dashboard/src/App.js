// src/App.js
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';

import Dashboard from './components/Dashboard';
import Devices from './components/Devices';
import Settings from './components/Settings';
import Roles from './components/Roles';
import RecentActivity from './components/RecentActivity';
import LoginScreen from './components/LoginScreen';
import MainLayout from './components/layout/MainLayout';
import DeviceDetail from './components/DeviceDetail';
import DeviceInventory from './pages/device/DeviceInventory';
import DeviceExtensions from './pages/device/DeviceExtensions';
import DeviceSoftware from './pages/device/DeviceSoftware';
import DeviceActions from './pages/device/DeviceActions';

axios.defaults.baseURL = 'http://192.168.32.87:5000'; // update if needed
axios.defaults.withCredentials = true;

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    axios.get('/api/me')
      .then((res) => {
        if (res.data.username) {
          setLoggedIn(true);
        }
        setCheckingSession(false);
      })
      .catch(() => {
        setLoggedIn(false);
        setCheckingSession(false);
      });
  }, []);

  const handleLogin = async (username, password, setError) => {
    try {
      const res = await axios.post('/api/login', { username, password });
      if (res.data.status === 'logged in') {
        setLoggedIn(true);
        setError('');
      } else {
        setError('Invalid credentials');
      }
    } catch {
      setError('Login failed');
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
  };

  if (checkingSession) return <div className="p-10 text-center">Checking session...</div>;

  if (!loggedIn) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout onLogout={handleLogout} />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="devices" element={<Devices />} />
          <Route path="settings" element={<Settings />} />
          <Route path="roles" element={<Roles />} />
          <Route path="activity" element={<RecentActivity />} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
          <Route path="/devices/:deviceId/*" element={<DeviceDetail />} />
	  <Route path="/devices/:deviceId/inventory" element={<DeviceInventory />} />
	  <Route path="/devices/:deviceId/extensions" element={<DeviceExtensions />} />
	  <Route path="/devices/:deviceId/software" element={<DeviceSoftware />} />
	  <Route path="/devices/:deviceId/actions" element={<DeviceActions />} />
	 </Route>
      </Routes>
    </Router>
  );
}

export default App;
