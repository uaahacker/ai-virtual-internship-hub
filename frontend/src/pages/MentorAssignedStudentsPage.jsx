import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { mentorService } from '../services/endpoints';
import { FiSearch, FiArrowRight } from 'react-icons/fi';

export default function MentorAssignedStudentsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name'); // name, progress, tasks
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.role !== 'Mentor') {
      navigate('/');
      return;
    }
    fetchStudents();
  }, [user, navigate]);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await mentorService.getAssignedStudents();
      if (response.data.success) {
        setStudents(response.data.data);
        setFilteredStudents(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to load students');
      }
    } catch (err) {
      setError('Error loading students');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
    let filtered = students.filter(s =>
      s.student_name.toLowerCase().includes(term.toLowerCase()) ||
      s.student_email.toLowerCase().includes(term.toLowerCase())
    );
    applySort(filtered);
  };

  const applySort = (data) => {
    let sorted = [...data];
    if (sortBy === 'name') {
      sorted.sort((a, b) => a.student_name.localeCompare(b.student_name));
    } else if (sortBy === 'progress') {
      sorted.sort((a, b) => b.progress_score - a.progress_score);
    } else if (sortBy === 'tasks') {
      sorted.sort((a, b) => b.completed_tasks_count - a.completed_tasks_count);
    }
    setFilteredStudents(sorted);
  };

  const handleSortChange = (newSort) => {
    setSortBy(newSort);
    applySort(
      students.filter(s =>
        s.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.student_email.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Assigned Students</h1>
          <p className="text-gray-600">
            Manage your {students.length} assigned student{students.length !== 1 ? 's' : ''}.
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
              <p className="text-gray-600">Loading students...</p>
            </div>
          </div>
        ) : students.length === 0 ? (
          <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
            <p className="text-gray-600 mb-4">No students assigned yet.</p>
            <button
              onClick={() => navigate('/mentor/dashboard')}
              className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
            >
              Back to Dashboard
            </button>
          </div>
        ) : (
          <>
            {/* Search and Sort */}
            <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Search Students</label>
                  <div className="relative">
                    <FiSearch className="absolute left-3 top-3 text-gray-400" size={18} />
                    <input
                      type="text"
                      placeholder="Name or email..."
                      value={searchTerm}
                      onChange={(e) => handleSearch(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => handleSortChange(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="name">Name (A-Z)</option>
                    <option value="progress">Progress (High to Low)</option>
                    <option value="tasks">Tasks Completed</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Students Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredStudents.map(student => (
                <div
                  key={student.student_id}
                  className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition"
                >
                  <div className="mb-4">
                    <h3 className="text-lg font-bold text-gray-900">{student.student_name}</h3>
                    <p className="text-sm text-gray-600 truncate">{student.student_email}</p>
                  </div>

                  {/* Strongest Domain */}
                  <div className="mb-4">
                    <p className="text-xs text-gray-600 uppercase font-medium">Strongest Domain</p>
                    <p className="text-sm font-semibold text-gray-900 mt-1">
                      {student.strongest_domain || 'N/A'}
                    </p>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-200">
                    <div>
                      <p className="text-xs text-gray-600">Progress</p>
                      <p className="text-xl font-bold text-gray-900">{student.progress_score}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Tasks Done</p>
                      <p className="text-xl font-bold text-gray-900">{student.completed_tasks_count}</p>
                    </div>
                  </div>

                  {/* Pending Reviews Badge */}
                  {student.pending_review_count > 0 && (
                    <div className="mb-4">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {student.pending_review_count} pending review{student.pending_review_count !== 1 ? 's' : ''}
                      </span>
                    </div>
                  )}

                  {/* Preferred Domains */}
                  {student.preferred_domains?.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs text-gray-600 mb-2">Preferred Domains</p>
                      <div className="flex flex-wrap gap-1">
                        {student.preferred_domains.slice(0, 2).map((domain, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                          >
                            {domain}
                          </span>
                        ))}
                        {student.preferred_domains.length > 2 && (
                          <span className="px-2 py-1 text-xs text-gray-500">
                            +{student.preferred_domains.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* View Button */}
                  <button
                    onClick={() => navigate(`/mentor/students/${student.student_id}`)}
                    className="w-full px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition flex items-center justify-center gap-2 font-medium"
                  >
                    View Details <FiArrowRight size={16} />
                  </button>
                </div>
              ))}
            </div>

            {filteredStudents.length === 0 && (
              <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
                <p className="text-gray-600">No students match your search.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
