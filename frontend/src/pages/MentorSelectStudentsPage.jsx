import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { mentorService, profileService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

const DOMAINS = [
  'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
  'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics', 'Digital Marketing', 'WordPress',
];

export default function MentorSelectStudentsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [availableStudents, setAvailableStudents] = useState([]);
  const [mentorProfile, setMentorProfile] = useState(null);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(null); // student_id being assigned
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [assignedIds, setAssignedIds] = useState(new Set());

  useEffect(() => {
    if (user?.role !== 'Mentor') {
      navigate('/');
      return;
    }
    loadInitialData();
  }, [user, navigate]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [profileRes, studentsRes] = await Promise.all([
        profileService.getMentorProfile(),
        mentorService.getAssignedStudents(),
      ]);
      if (profileRes.data.success) {
        setMentorProfile(profileRes.data.data);
      }
      if (studentsRes.data.success) {
        const ids = new Set(studentsRes.data.data.map(s => s.student_id));
        setAssignedIds(ids);
      }
      await fetchAvailable('');
    } catch (err) {
      setError('Failed to load data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailable = async (domain) => {
    try {
      const res = await mentorService.getAvailableStudents(domain);
      if (res.data.success) {
        setAvailableStudents(res.data.data);
      } else {
        setError(res.data.error?.message || 'Failed to load students');
      }
    } catch (err) {
      setError('Error fetching available students');
      console.error(err);
    }
  };

  const handleDomainChange = async (domain) => {
    setSelectedDomain(domain);
    setError('');
    await fetchAvailable(domain);
  };

  const handleAssign = async (student) => {
    setAssigning(student.student_id);
    setError('');
    setSuccessMsg('');
    try {
      const res = await mentorService.assignStudent(student.student_id);
      if (res.data.success) {
        setSuccessMsg(`${student.student_name} has been added to your students!`);
        setAssignedIds(prev => new Set([...prev, student.student_id]));
        // Remove from available list
        setAvailableStudents(prev => prev.filter(s => s.student_id !== student.student_id));
      } else {
        setError(res.data.error?.message || 'Failed to assign student');
      }
    } catch (err) {
      setError('Error assigning student');
      console.error(err);
    } finally {
      setAssigning(null);
    }
  };

  const capacityUsed = assignedIds.size;
  const maxStudents = mentorProfile?.max_students || 10;
  const atCapacity = capacityUsed >= maxStudents;

  return (
    <DashboardLayout>
      <div className="pb-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-1">Select Students</h1>
          <p className="text-gray-500">
            Browse students looking for a mentor. Assign students that match your expertise.
          </p>
        </div>

        {/* Capacity Bar */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Student Capacity</span>
            <span className="text-sm font-bold text-gray-900">{capacityUsed} / {maxStudents}</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${atCapacity ? 'bg-red-500' : 'bg-gray-900'}`}
              style={{ width: `${Math.min(100, (capacityUsed / maxStudents) * 100)}%` }}
            />
          </div>
          {atCapacity && (
            <p className="text-xs text-red-600 font-medium mt-2">
              ⚠️ You've reached your maximum capacity. Manage existing students first.
            </p>
          )}
          {mentorProfile?.expertise_domains?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              <span className="text-xs text-gray-500">Your domains:</span>
              {mentorProfile.expertise_domains.map(d => (
                <span key={d} className="px-2.5 py-0.5 bg-gray-900 text-white text-xs rounded-full">{d}</span>
              ))}
            </div>
          )}
        </div>

        {/* Success / Error */}
        {successMsg && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm font-medium">
            ✅ {successMsg}
          </div>
        )}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Domain Filter */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleDomainChange('')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedDomain === ''
                  ? 'bg-gray-900 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              All Domains
            </button>
            {DOMAINS.map(d => (
              <button
                key={d}
                onClick={() => handleDomainChange(d)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  selectedDomain === d
                    ? 'bg-gray-900 text-white'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        {/* Students Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 animate-pulse">
                <div className="h-5 bg-gray-100 rounded w-2/3 mb-2" />
                <div className="h-4 bg-gray-100 rounded w-1/2 mb-4" />
                <div className="h-8 bg-gray-100 rounded w-full" />
              </div>
            ))}
          </div>
        ) : availableStudents.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="text-4xl mb-3">🔍</div>
            <p className="font-medium text-gray-700">No available students found</p>
            <p className="text-sm text-gray-400 mt-1">
              {selectedDomain
                ? `No unassigned students in "${selectedDomain}" right now.`
                : 'All students already have mentors, or no students match your expertise.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableStudents.map(student => {
              const isAssigned = assignedIds.has(student.student_id);
              return (
                <div key={student.student_id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-sm transition-shadow">
                  {/* Student Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 font-bold">
                        {student.student_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 text-sm">{student.student_name}</p>
                        <p className="text-xs text-gray-400">{student.student_email}</p>
                      </div>
                    </div>
                  </div>

                  {/* Domain/Skills */}
                  <div className="mb-3">
                    {student.strongest_domain ? (
                      <span className="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
                        🎯 {student.strongest_domain}
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">No domain yet</span>
                    )}
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <div className="font-bold text-gray-900">{Math.round(student.progress_score || 0)}%</div>
                      <div className="text-gray-500">Progress</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <div className="font-bold text-gray-900">{student.completed_tasks_count || 0}</div>
                      <div className="text-gray-500">Tasks Done</div>
                    </div>
                  </div>

                  {/* Cluster label */}
                  {student.cluster_label && (
                    <div className="mb-3">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                        student.cluster_label === 'Expert' ? 'bg-green-100 text-green-700' :
                        student.cluster_label === 'Competent' ? 'bg-blue-100 text-blue-700' :
                        student.cluster_label === 'Developing' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {student.cluster_label}
                      </span>
                    </div>
                  )}

                  {/* Assign Button */}
                  {isAssigned ? (
                    <div className="w-full py-2 text-center text-xs text-green-700 font-semibold bg-green-50 rounded-lg border border-green-200">
                      ✓ Already your student
                    </div>
                  ) : (
                    <button
                      onClick={() => handleAssign(student)}
                      disabled={atCapacity || assigning === student.student_id}
                      className="w-full py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {assigning === student.student_id ? 'Assigning...' : 'Assign to Me'}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
