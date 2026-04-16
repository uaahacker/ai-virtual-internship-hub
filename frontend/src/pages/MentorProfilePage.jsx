import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { profileService } from '../services/endpoints';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { FiEdit2, FiSave, FiX, FiUser, FiTarget, FiUsers, FiStar, FiCalendar } from 'react-icons/fi';

export default function MentorProfilePage() {
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
      const res = await profileService.getMentorProfile();
      setProfile(res.data.data);
      setFormData({
        bio: res.data.data.bio || '',
        expertise_domains: res.data.data.expertise_domains || [],
        max_students: res.data.data.max_students || 10,
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
      const res = await profileService.updateMentorProfile(formData);
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

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mentor Profile</h1>
          <p className="text-gray-500 mt-1">Manage your mentoring profile and expertise.</p>
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
                  placeholder="Tell students about your mentoring style and experience..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>

              {/* Expertise Domains */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <FiTarget className="inline mr-2" /> Expertise Domains (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.expertise_domains.join(', ')}
                  onChange={(e) => handleArrayInput('expertise_domains', e.target.value)}
                  placeholder="e.g., Programming, Web Development, Data Science"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Max Students */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  <FiUsers className="inline mr-2" /> Maximum Students
                </label>
                <input
                  type="number"
                  name="max_students"
                  value={formData.max_students}
                  onChange={handleInputChange}
                  min="1"
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
                  <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center">
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

              {/* Expertise Domains */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FiTarget />
                  Areas of Expertise
                </h3>
                {profile.expertise_domains && profile.expertise_domains.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.expertise_domains.map((domain, idx) => (
                      <span
                        key={idx}
                        className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-medium"
                      >
                        {domain}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No expertise domains added yet.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Stats Sidebar */}
        <div className="space-y-4">
          {/* Students */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiUsers />
              Students
            </h3>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">
                {profile.current_student_count}/{profile.max_students}
              </div>
              <p className="text-xs text-gray-500">Current / Max students</p>
            </div>
            <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{
                  width: `${(profile.current_student_count / profile.max_students) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Rating */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FiStar />
              Rating
            </h3>
            <div className="text-center">
              <div className="text-4xl font-bold text-yellow-500 mb-1">
                {profile.rating.toFixed(1)}
              </div>
              <p className="text-xs text-gray-500">Out of 5.0</p>
            </div>
          </div>

          {/* Expertise Summary */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Expertise</h3>
            <div className="text-xs text-gray-600">
              <p className="mb-2">
                <strong>Domains:</strong>{' '}
                {profile.expertise_domains && profile.expertise_domains.length > 0
                  ? profile.expertise_domains.length
                  : 0}
              </p>
              <p className="mb-2">
                <strong>Max Capacity:</strong> {profile.max_students}
              </p>
              <p>
                <strong>Availability:</strong>{' '}
                {profile.current_student_count < profile.max_students ? 'Available' : 'Full'}
              </p>
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
