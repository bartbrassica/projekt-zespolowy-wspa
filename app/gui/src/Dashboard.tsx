import React from 'react'
import { FileText, Lock, Key, Shield } from 'lucide-react'

const Dashboard: React.FC = () => {
  const stats = [
    { name: 'Total Documents', value: '12', icon: FileText, color: 'text-blue-600' },
    { name: 'Passwords Stored', value: '24', icon: Lock, color: 'text-green-600' },
    { name: 'API Keys', value: '8', icon: Key, color: 'text-purple-600' },
    { name: 'Security Score', value: '95%', icon: Shield, color: 'text-indigo-600' },
  ]

  return (
    <div className="px-4 sm:px-0">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Dashboard</h1>
      <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
        Welcome to your secure digital lockbox. Your data is encrypted and protected.
      </p>

      {/* Stats Grid */}
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.name}
              className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        {stat.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                          {stat.value}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white">Recent Activity</h2>
        <div className="mt-4 bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {[
              { action: 'Added new password', item: 'GitHub Account', time: '2 hours ago' },
              { action: 'Updated document', item: 'Tax Returns 2024', time: '5 hours ago' },
              { action: 'Created API key', item: 'Production Server', time: '1 day ago' },
              { action: 'Deleted password', item: 'Old Email Account', time: '2 days ago' },
            ].map((activity, index) => (
              <li key={index} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {activity.action}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{activity.item}</p>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{activity.time}</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Dashboard