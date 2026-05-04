import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import TaskCard from '../components/TaskCard';
import DashboardLayout from '../components/DashboardLayout';

export default function RecommendedTasksPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('score'); // score, domain, difficulty
  const [filterDomain, setFilterDomain] = useState('');

  const DOMAINS = [
    'Graphic Design',
    'Content Writing',
    'Programming',
    'Freelancing',
    'E-Commerce',
    'QuickBooks',
    'AutoCAD',
    'Data Analytics',
    'Digital Marketing',
    'WordPress',
  ];

  useEffect(() => {
    if (user?.role !== 'Student') {
      navigate('/');
      return;
    }
    fetchRecommendedTasks();
  }, [user, navigate]);

  const fetchRecommendedTasks = async () => {
    try {
      setLoading(true);
      const response = await taskService.getRecommendations();
      if (response.data.success) {
        setTasks(response.data.data || []);
      } else {
        setError(response.data.error?.message || 'Failed to load recommendations');
      }
    } catch (err) {
      setError('Error loading recommendations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecommendationResponse = async (assignmentId, accept) => {
    try {
      setError('');
      const response = await taskService.acceptTask(assignmentId, accept);
      if (response.data.success) {
        // Remove task from list
        setTasks(tasks.filter(task => task.id !== assignmentId));
        // Show success message
        toast.success(
          accept
            ? 'Task accepted! Check "My Tasks" to start working on it.'
            : 'Recommendation declined.'
        );
      } else {
        setError(response.data.error?.message || response.data.error || 'Failed to process recommendation');
      }
    } catch (err) {
      setError('Error processing recommendation');
      console.error(err);
    }
  };

  const getSortedTasks = () => {
    let sorted = [...tasks];
    if (sortBy === 'score') {
      sorted.sort((a, b) => (b.recommended_score || 0) - (a.recommended_score || 0));
    } else if (sortBy === 'domain') {
      sorted.sort((a, b) => (a.task_domain || '').localeCompare(b.task_domain || ''));
    } else if (sortBy === 'difficulty') {
      const diffOrder = { 'Beginner': 1, 'Intermediate': 2, 'Advanced': 3 };
      sorted.sort((a, b) => (diffOrder[a.task_difficulty] || 0) - (diffOrder[b.task_difficulty] || 0));
    }
    return sorted;
  };

  const getFilteredTasks = () => {
    let filtered = getSortedTasks();
    if (filterDomain && filterDomain !== '') {
      filtered = filtered.filter(task => task.task_domain === filterDomain);
    }
    return filtered;
  };

  const filteredTasks = getFilteredTasks();

  return (
    <DashboardLayout>
      <div className="pb-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Recommended Tasks</h1>
          <p className="text-gray-600">
            Based on your assessment results, we've selected {tasks.length} tasks tailored to your skills and interests.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-600">Loading recommendations...</p>
            </div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
            <p className="text-gray-600 mb-4">No recommendations available yet.</p>
            <p className="text-sm text-gray-500">
              Complete an assessment to receive personalized task recommendations.
            </p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="score">Match Score (High to Low)</option>
                    <option value="domain">Domain</option>
                    <option value="difficulty">Difficulty Level</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Domain</label>
                  <select
                    value={filterDomain}
                    onChange={(e) => setFilterDomain(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="">All Domains</option>
                    {DOMAINS.map(domain => (
                      <option key={domain} value={domain}>{domain}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredTasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isRecommended={true}
                  matchScore={task.recommended_score}
                  reason={task.recommendation_reason}
                  explanation={task.recommendation_explanation}
                  onAccept={() => handleRecommendationResponse(task.id, true)}
                  onDecline={() => handleRecommendationResponse(task.id, false)}
                />
              ))}
            </div>

            {filteredTasks.length === 0 && (
              <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
                <p className="text-gray-600">No tasks match your filter.</p>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
