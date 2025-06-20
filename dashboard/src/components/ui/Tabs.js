import React, { useState } from 'react';

export function Tabs({ tabs }) {
  const [activeTab, setActiveTab] = useState(tabs[0].label);

  return (
    <div>
      <div className="flex space-x-2 border-b mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.label}
            className={`py-2 px-4 text-sm ${
              activeTab === tab.label ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'
            }`}
            onClick={() => setActiveTab(tab.label)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div>
        {tabs.find((tab) => tab.label === activeTab)?.content}
      </div>
    </div>
  );
}

