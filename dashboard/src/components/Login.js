import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

function Login({ setLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const res = await axios.post('/api/login', { username, password });
      if (res.data.status === 'logged in') setLoggedIn(true);
    } catch {
      alert('Login failed');
      const res = await axios.post(
        'http://192.168.32.87:5000/api/login', // Use your backend IP
        { username, password },
        { withCredentials: true }
      );
      if (res.data.status === 'logged in') {
        setLoggedIn(true);
      } else {
        alert('Login failed: ' + res.data.status);
      }
    } catch (err) {
      alert('Login failed: Server error');
      console.error(err);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>System Monitor Login</h2>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
        <button onClick={handleLogin}>Login</button>
      </div>
    <div className="login-box">
      <input
        value={username}
        onChange={e => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;
