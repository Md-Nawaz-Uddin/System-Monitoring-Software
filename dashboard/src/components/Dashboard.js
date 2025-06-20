import React from 'react';
import Devices from './Devices';
import CommandLog from './CommandLog';

function Dashboard() {
  return (
    <div>
      <h2>Dashboard</h2>
      <Devices />
      <CommandLog />
    </div>
  );
}
export default Dashboard;

