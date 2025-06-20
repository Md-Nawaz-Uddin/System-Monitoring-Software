import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Dashboard from './Dashboard';

axios.defaults.baseURL = 'http://192.168.32.87:5000';
axios.defaults.withCredentials = true;

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);

  // ✅ Check session on mount
  useEffect(() => {
    axios.get('/api/me')
      .then(res => {
        if (res.data.username) {
          setLoggedIn(true);
        }
      })
      .catch(err => {
        setLoggedIn(false); // Not logged in
      });
  }, []);

  const handleLogin = async () => {
    try {
      const res = await axios.post('/api/login', { username, password });
      if (res.data.status === 'logged in') {
        setLoggedIn(true);
        setError('');
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Login failed');
    }
  };

  if (loggedIn) return <Dashboard />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-700">System Monitor Login</h2>

        <input
          className="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          className="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
        <button
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
          onClick={handleLogin}
        >
          Login
        </button>
      </div>
    </div>
  );
}

export default App;

