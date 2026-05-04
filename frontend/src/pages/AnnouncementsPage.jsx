import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import DashboardLayout from '../components/DashboardLayout';
import { useAuth } from '../contexts/AuthContext';
import { announcementService } from '../services/endpoints';

const AUDIENCE_OPTIONS = [
  { value: 'All', label: 'Everyone' },
  { value: 'Students', label: 'Students Only' },
  { value: 'Mentors', label: 'Mentors Only' },
];

export default function AnnouncementsPage() {
  const { user } = useAuth();
  const role = user?.role;
  const canCreate = role === 'Admin' || role === 'Mentor';

  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', content: '', audience: 'All' });
  const [submitting, setSubmitting] = useState(false);

  const loadAnnouncements = useCallback(async () => {
    setLoading(true);
    try {
      const res = await announcementService.list();
      if (res.data.success) setAnnouncements(res.data.data || []);
    } catch {
      toast.error('Failed to load announcements.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAnnouncements(); }, [loadAnnouncements]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.content.trim()) {
      toast.error('Title and content are required.');
      return;
    }
    setSubmitting(true);
    try {
      const payload = { ...form };
      if (role === 'Mentor') payload.audience = 'Students';
      const res = await announcementService.create(payload);
      if (res.data.success) {
        toast.success('Announcement posted!');
        setForm({ title: '', content: '', audience: 'All' });
        setShowForm(false);
        loadAnnouncements();
      } else {
        toast.error(res.data.error || 'Failed to post.');
      }
    } catch {
      toast.error('Error posting announcement.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this announcement?')) return;
    try {
      const res = await announcementService.delete(id);
      if (res.data.success) {
        toast.success('Deleted.');
        setAnnouncements((prev) => prev.filter((a) => a.id !== id));
      } else {
        toast.error(res.data.error || 'Failed to delete.');
      }
    } catch {
      toast.error('Error deleting announcement.');
    }
  };

  const audienceBadgeClass = (audience) => {
    if (audience === 'All') return 'bg-blue-100 text-blue-700';
    if (audience === 'Students') return 'bg-green-100 text-green-700';
    return 'bg-purple-100 text-purple-700';
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Announcements</h1>
            <p className="text-sm text-gray-500 mt-1">Stay updated with the latest news</p>
          </div>
          {canCreate && !showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <span className="text-base">📢</span> New Announcement
            </button>
          )}
        </div>

        {/* Create Form */}
        {canCreate && showForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Post Announcement</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="Announcement title..."
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <textarea
                  value={form.content}
                  onChange={(e) => setForm({ ...form, content: e.target.value })}
                  placeholder="Write your announcement here..."
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
                />
              </div>
              {role === 'Admin' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Audience</label>
                  <select
                    value={form.audience}
                    onChange={(e) => setForm({ ...form, audience: e.target.value })}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  >
                    {AUDIENCE_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
              )}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
                >
                  {submitting ? 'Posting...' : 'Post'}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowForm(false); setForm({ title: '', content: '', audience: 'All' }); }}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium px-5 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Announcement List */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading announcements...</div>
        ) : announcements.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
            <p className="text-4xl mb-3">📭</p>
            <p className="text-gray-500 font-medium">No announcements yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {announcements.map((ann) => (
              <div key={ann.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <h3 className="font-semibold text-gray-800 text-base">{ann.title}</h3>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${audienceBadgeClass(ann.audience)}`}>
                        {ann.audience === 'All' ? 'Everyone' : ann.audience}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">{ann.content}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      By <span className="font-medium text-gray-500">{ann.created_by_name}</span>
                      {ann.created_by_role && ` (${ann.created_by_role})`}
                      {' · '}
                      {new Date(ann.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  {(role === 'Admin' || ann.is_own) && (
                    <button
                      onClick={() => handleDelete(ann.id)}
                      className="flex-shrink-0 text-red-400 hover:text-red-600 transition-colors p-1"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
