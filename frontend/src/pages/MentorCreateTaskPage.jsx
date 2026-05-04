import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

const DOMAINS = [
  'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
  'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics',
  'Digital Marketing', 'WordPress',
];
const DIFFICULTIES = ['Beginner', 'Intermediate', 'Advanced'];
const TASK_TYPES = [
  { value: 'Design', label: 'Design Project' },
  { value: 'Development', label: 'Development Project' },
  { value: 'Content', label: 'Content Creation' },
  { value: 'Analysis', label: 'Data Analysis' },
  { value: 'Marketing', label: 'Marketing Campaign' },
  { value: 'Research', label: 'Research Task' },
  { value: 'Other', label: 'Other' },
];

const EMPTY_FORM = {
  title: '',
  description: '',
  domain: '',
  difficulty: 'Beginner',
  task_type: 'Design',
  required_skills: [],
  learning_outcomes: [],
  estimated_duration: 60,
  is_active: true,
};

export default function MentorCreateTaskPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { taskId } = useParams();           // present when editing
  const isEdit = Boolean(taskId);

  const [form, setForm] = useState(EMPTY_FORM);
  const [skillInput, setSkillInput] = useState('');
  const [outcomeInput, setOutcomeInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(isEdit);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.role !== 'Mentor') { navigate('/'); return; }
    if (isEdit) loadTask();
  }, [user, navigate, taskId]);

  const loadTask = async () => {
    try {
      setFetchLoading(true);
      const res = await taskService.getMentorTaskDetail(taskId);
      if (res.data.success) {
        const t = res.data.data;
        setForm({
          title: t.title || '',
          description: t.description || '',
          domain: t.domain || '',
          difficulty: t.difficulty || 'Beginner',
          task_type: t.task_type || 'Project',
          required_skills: Array.isArray(t.required_skills) ? t.required_skills : [],
          learning_outcomes: Array.isArray(t.learning_outcomes) ? t.learning_outcomes : [],
          estimated_duration: t.estimated_duration || 60,
          is_active: t.is_active !== false,
        });
      } else {
        setError(res.data.error || 'Task not found');
      }
    } catch (err) {
      setError('Failed to load task');
    } finally {
      setFetchLoading(false);
    }
  };

  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const addSkill = () => {
    const v = skillInput.trim();
    if (v && !form.required_skills.includes(v)) {
      set('required_skills', [...form.required_skills, v]);
    }
    setSkillInput('');
  };

  const removeSkill = (skill) => set('required_skills', form.required_skills.filter(s => s !== skill));

  const addOutcome = () => {
    const v = outcomeInput.trim();
    if (v && !form.learning_outcomes.includes(v)) {
      set('learning_outcomes', [...form.learning_outcomes, v]);
    }
    setOutcomeInput('');
  };

  const removeOutcome = (o) => set('learning_outcomes', form.learning_outcomes.filter(x => x !== o));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!form.title.trim()) return setError('Title is required.');
    if (!form.description.trim()) return setError('Description is required.');
    if (!form.domain) return setError('Please select a domain.');
    if (!form.estimated_duration || form.estimated_duration < 5) return setError('Duration must be at least 5 minutes.');

    try {
      setLoading(true);
      const res = isEdit
        ? await taskService.updateTask(taskId, form)
        : await taskService.create(form);

      if (res.data.success) {
        navigate('/mentor/tasks');
      } else {
        const err = res.data.error;
        setError(typeof err === 'object' ? JSON.stringify(err) : err || 'Save failed');
      }
    } catch (err) {
      setError('Failed to save task');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (fetchLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto pb-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate('/mentor/tasks')}
            className="text-gray-500 hover:text-gray-800 transition text-sm font-medium"
          >
            ← Back to My Tasks
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isEdit ? 'Edit Task' : 'Create New Task'}
            </h1>
            <p className="text-gray-500 mt-1 text-sm">
              {isEdit ? 'Update your task details below.' : 'Fill in the details to post a new task for students.'}
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Task Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={form.title}
                  onChange={e => set('title', e.target.value)}
                  placeholder="e.g. Build a Responsive Landing Page"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={form.description}
                  onChange={e => set('description', e.target.value)}
                  rows={4}
                  placeholder="Describe what the student needs to do, what resources they can use, expected deliverables..."
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 resize-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Domain <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={form.domain}
                    onChange={e => set('domain', e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="">Select domain</option>
                    {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Difficulty</label>
                  <select
                    value={form.difficulty}
                    onChange={e => set('difficulty', e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    {DIFFICULTIES.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Task Type</label>
                  <select
                    value={form.task_type}
                    onChange={e => set('task_type', e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    {TASK_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Estimated Duration (minutes) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="10000"
                    value={form.estimated_duration}
                    onChange={e => set('estimated_duration', parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                  />
                </div>
                <div className="flex items-end pb-1">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.is_active}
                      onChange={e => set('is_active', e.target.checked)}
                      className="w-4 h-4 rounded border-gray-300 accent-gray-900"
                    />
                    <span className="text-sm font-medium text-gray-700">Active (visible to students)</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Required Skills */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="font-semibold text-gray-900 mb-1">Required Skills</h2>
            <p className="text-xs text-gray-500 mb-4">Skills students need to complete this task</p>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={skillInput}
                onChange={e => setSkillInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addSkill(); } }}
                placeholder="e.g. HTML, CSS, Photoshop"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
              />
              <button
                type="button"
                onClick={addSkill}
                className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {form.required_skills.map((s, i) => (
                <span key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 border border-blue-200 text-blue-800 text-sm rounded-full">
                  {s}
                  <button type="button" onClick={() => removeSkill(s)} className="text-blue-500 hover:text-red-600 font-bold leading-none">×</button>
                </span>
              ))}
              {form.required_skills.length === 0 && (
                <p className="text-sm text-gray-400">No skills added yet</p>
              )}
            </div>
          </div>

          {/* Learning Outcomes */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="font-semibold text-gray-900 mb-1">Learning Outcomes</h2>
            <p className="text-xs text-gray-500 mb-4">What will students learn from this task?</p>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={outcomeInput}
                onChange={e => setOutcomeInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addOutcome(); } }}
                placeholder="e.g. Master responsive design, Understand CSS Grid"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
              />
              <button
                type="button"
                onClick={addOutcome}
                className="px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition"
              >
                Add
              </button>
            </div>
            <div className="space-y-2">
              {form.learning_outcomes.map((o, i) => (
                <div key={i} className="flex items-center gap-2 p-2.5 bg-green-50 border border-green-200 rounded-lg">
                  <span className="text-green-600 text-sm">✓</span>
                  <span className="flex-1 text-sm text-gray-800">{o}</span>
                  <button type="button" onClick={() => removeOutcome(o)} className="text-gray-400 hover:text-red-600 font-bold">×</button>
                </div>
              ))}
              {form.learning_outcomes.length === 0 && (
                <p className="text-sm text-gray-400">No outcomes added yet</p>
              )}
            </div>
          </div>

          {/* Submit */}
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={() => navigate('/mentor/tasks')}
              className="px-5 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-700 disabled:opacity-50 transition flex items-center gap-2"
            >
              {loading && <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
              {isEdit ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
