import React, { useState } from 'react';
import axios from 'axios';

function Login({ setLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const res = await axios.post('/api/login', { username, password });
      if (res.data.status === 'logged in') setLoggedIn(true);
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="login-box">
      <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;
