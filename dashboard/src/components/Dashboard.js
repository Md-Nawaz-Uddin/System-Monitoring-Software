import React from 'react';
import DeviceTable from './DeviceTable';
import CommandLog from './CommandLog';

function Dashboard() {
  return (
    <div>
      <h1>System Monitoring Dashboard</h1>
      <DeviceTable />
      <CommandLog />
    </div>
  );
}

export default Dashboard;
