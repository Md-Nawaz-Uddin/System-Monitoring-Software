import React from 'react';
import DeviceTable from './DeviceTable';
import CommandLog from './CommandLog';

function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">🖥️ System Monitoring Dashboard</h1>
        <p className="text-gray-500">Live view of devices and audit logs</p>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">📋 Device Status</h2>
          <DeviceTable />
        </section>

        <section className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">🧾 Command Logs</h2>
          <CommandLog />
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
