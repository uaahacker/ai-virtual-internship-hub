import DashboardLayout from '../components/DashboardLayout';
import { useAuth } from '../contexts/AuthContext';
import { FiUsers, FiClipboard, FiMessageSquare } from 'react-icons/fi';

export default function MentorDashboard() {
  const { user } = useAuth();

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.name}!
        </h1>
        <p className="text-gray-500 mt-1">Mentor Dashboard — manage your assigned students and tasks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          { label: 'Assigned Students', value: '—', icon: FiUsers, color: 'text-blue-600 bg-blue-100' },
          { label: 'Tasks Created', value: '—', icon: FiClipboard, color: 'text-green-600 bg-green-100' },
          { label: 'Pending Reviews', value: '—', icon: FiMessageSquare, color: 'text-yellow-600 bg-yellow-100' },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-xl shadow-sm p-6 flex items-center gap-4">
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${card.color}`}>
              <card.icon size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              <p className="text-sm text-gray-500">{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Placeholder sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Assigned Students</h2>
          <div className="text-center py-12 text-gray-400">
            <FiUsers className="mx-auto mb-3" size={40} />
            <p>Student assignments will appear here once the Tasks module is implemented.</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Submissions to Review</h2>
          <div className="text-center py-12 text-gray-400">
            <FiClipboard className="mx-auto mb-3" size={40} />
            <p>Pending submissions will appear here in future versions.</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
