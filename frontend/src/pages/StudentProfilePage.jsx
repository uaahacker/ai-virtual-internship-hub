import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { profileService } from '../services/endpoints';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { FiEdit2, FiSave, FiX, FiUser, FiTarget, FiBarChart2, FiCalendar } from 'react-icons/fi';

export default function StudentProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await profileService.getStudentProfile();
      setProfile(res.data.data);
      setFormData({
        bio: res.data.data.bio || '',
        selected_skills: res.data.data.selected_skills || [],
        preferred_domains: res.data.data.preferred_domains || [],
      });
    } catch (err) {
      toast.error('Failed to load profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleArrayInput = (field, value) => {
    const items = value.split(',').map(item => item.trim()).filter(item => item);
    setFormData({ ...formData, [field]: items });
  };

  const handleSave = async () => {
    try {
      const res = await profileService.updateStudentProfile(formData);
      setProfile(res.data.data);
      setEditing(false);
      toast.success('Profile updated successfully!');
    } catch (err) {
      toast.error('Failed to update profile.');
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="text-center py-16 text-gray-400">Loading profile...</div>
      </DashboardLayout>
    );
  }

  if (!profile) {
    return (
      <DashboardLayout>
        <div className="text-center py-16 text-gray-400">Profile not found.</div>
      </DashboardLayout>
    );
  }

  const levelColor = (level) => {
    if (level === 'Advanced') return 'text-green-600 bg-green-100';
    if (level === 'Intermediate') return 'text-yellow-600 bg-yellow-100';
    return 'text-red-500 bg-red-100';
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
          <p className="text-gray-500 mt-1">Manage your learning profile and preferences.</p>
        </div>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <FiEdit2 size={18} />
            Edit Profile
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Profile Card */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-8">
          {editing ? (
            // Edit Mode
            <div className="space-y-6">
              {/* Bio */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <FiUser className="inline mr-2" /> About You
                </label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Tell us about yourself..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>

              {/* Selected Skills */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <FiTarget className="inline mr-2" /> Skills (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.selected_skills.join(', ')}
                  onChange={(e) => handleArrayInput('selected_skills', e.target.value)}
                  placeholder="e.g., JavaScript, React, Web Design"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Preferred Domains */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <FiBarChart2 className="inline mr-2" /> Preferred Domains (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.preferred_domains.join(', ')}
                  onChange={(e) => handleArrayInput('preferred_domains', e.target.value)}
                  placeholder="e.g., Programming, Web Dev, AI"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleSave}
                  className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex-1 justify-center"
                >
                  <FiSave size={18} />
                  Save Changes
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="flex items-center gap-2 px-6 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition flex-1 justify-center"
                >
                  <FiX size={18} />
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            // View Mode
            <div className="space-y-8">
              {/* User Info */}
              <div className="border-b border-gray-200 pb-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
                    <FiUser className="text-white" size={32} />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{user?.name}</h2>
                    <p className="text-gray-500">{user?.email}</p>
                  </div>
                </div>
              </div>

              {/* Bio */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FiUser />
                  About
                </h3>
                <p className="text-gray-600 whitespace-pre-wrap">
                  {profile.bio || 'No bio added yet.'}
                </p>
              </div>

              {/* Skills */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FiTarget />
                  Skills
                </h3>
                {profile.selected_skills && profile.selected_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.selected_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No skills added yet.</p>
                )}
              </div>

              {/* Preferred Domains */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FiBarChart2 />
                  Preferred Domains
                </h3>
                {profile.preferred_domains && profile.preferred_domains.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.preferred_domains.map((domain, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium"
                      >
                        {domain}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No preferred domains yet.</p>
                )}
              </div>

              {/* Assigned Mentor */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FiUser />
                  Assigned Mentor
                </h3>
                {profile.mentor_name ? (
                  <p className="text-gray-600 font-medium">{profile.mentor_name}</p>
                ) : (
                  <p className="text-gray-500">No mentor assigned yet.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Stats Sidebar */}
        <div className="space-y-4">
          {/* Progress */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiBarChart2 />
              Progress
            </h3>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-1">
                {Math.round(profile.progress_score)}%
              </div>
              <p className="text-sm text-gray-500">Overall Progress</p>
            </div>
          </div>

          {/* Assessment Summary */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Assessment Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Strongest Domain</span>
                <span className="text-sm font-bold text-gray-900">
                  {profile.strongest_domain || 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Weakest Domain</span>
                <span className="text-sm font-bold text-gray-900">
                  {profile.weakest_domain || 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Tasks Completed</span>
                <span className="text-sm font-bold text-gray-900">
                  {profile.completed_tasks_count}
                </span>
              </div>
            </div>
          </div>

          {/* Profile Meta */}
          <div className="bg-gray-50 rounded-xl shadow-sm p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiCalendar />
              Meta
            </h3>
            <div className="space-y-2 text-xs text-gray-600">
              <p>
                <strong>Created:</strong> {new Date(profile.created_at).toLocaleDateString()}
              </p>
              <p>
                <strong>Updated:</strong> {new Date(profile.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
