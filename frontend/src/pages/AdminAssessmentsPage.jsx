import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { adminService } from '../services/endpoints';
import { Badge } from '../components/CardComponents';
import ConfirmModal from '../components/ConfirmModal';
import { toast } from 'react-toastify';

const DOMAINS = [
  'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
  'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics', 'Digital Marketing', 'WordPress',
];

// ── Assessment Create/Edit Modal ───────────────────────────────
function AssessmentModal({ assessment, onClose, onSave }) {
  const isEdit = !!assessment?.id;
  const [form, setForm] = useState({
    title: assessment?.title || '',
    domain: assessment?.domain || DOMAINS[0],
    description: assessment?.description || '',
    time_limit: assessment?.time_limit || '',
    is_active: assessment?.is_active !== false,
  });
  const [saving, setSaving] = useState(false);

  const handle = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((p) => ({ ...p, [name]: type === 'checkbox' ? checked : value }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        time_limit: form.time_limit ? parseInt(form.time_limit) : null,
      };
      if (isEdit) {
        await adminService.updateAssessment(assessment.id, payload);
        toast.success('Assessment updated');
      } else {
        await adminService.createAssessment(payload);
        toast.success('Assessment created');
      }
      onSave();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to save assessment');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">{isEdit ? 'Edit Assessment' : 'New Assessment'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={submit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Title *</label>
            <input name="title" value={form.title} onChange={handle} required
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Domain *</label>
              <select name="domain" value={form.domain} onChange={handle}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {DOMAINS.map((d) => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Time Limit (mins)</label>
              <input name="time_limit" type="number" min="1" value={form.time_limit} onChange={handle}
                placeholder="Optional"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea name="description" value={form.description} onChange={handle} rows={3}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" name="is_active" checked={form.is_active} onChange={handle}
              className="w-4 h-4 text-blue-600 rounded" />
            <span className="text-sm text-slate-700">Active (visible to students)</span>
          </label>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 transition">Cancel</button>
            <button type="submit" disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">
              {saving ? 'Saving...' : isEdit ? 'Save' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Question Management Panel ──────────────────────────────────
function QuestionPanel({ assessment, onClose, onUpdated }) {
  const [questions, setQuestions] = useState(assessment.questions || []);
  const [form, setForm] = useState({ text: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: 'A' });
  const [saving, setSaving] = useState(false);
  const [confirmModal, setConfirmModal] = useState(null);

  const handle = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const addQuestion = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await adminService.addQuestion(assessment.id, form);
      setQuestions((p) => [...p, res.data.data]);
      setForm({ text: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_option: 'A' });
      toast.success('Question added');
      onUpdated();
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to add question');
    } finally {
      setSaving(false);
    }
  };

  const removeQuestion = (q) => {
    setConfirmModal({
      title: 'Delete Question',
      message: `Delete question: "${q.text.slice(0, 60)}..."?`,
      danger: true,
      confirmLabel: 'Delete',
      onConfirm: async () => {
        await adminService.deleteQuestion(assessment.id, q.id);
        setQuestions((p) => p.filter((x) => x.id !== q.id));
        toast.success('Question deleted');
        onUpdated();
      },
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 shrink-0">
          <div>
            <h2 className="text-lg font-bold text-slate-900">📝 Questions — {assessment.title}</h2>
            <p className="text-xs text-slate-500">{questions.length} questions</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {questions.length === 0 ? (
            <p className="text-center text-slate-400 py-8">No questions yet. Add some below.</p>
          ) : (
            questions.map((q, i) => (
              <div key={q.id} className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900">Q{i + 1}. {q.text}</p>
                    <div className="grid grid-cols-2 gap-1 mt-2">
                      {['A', 'B', 'C', 'D'].map((opt) => (
                        <span key={opt} className={`text-xs px-2 py-1 rounded ${q.correct_option === opt ? 'bg-green-100 text-green-800 font-semibold' : 'text-slate-500'}`}>
                          {opt}. {q[`option_${opt.toLowerCase()}`]}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button onClick={() => removeQuestion(q)}
                    className="shrink-0 p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition text-base">🗑️</button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Add Question Form */}
        <div className="border-t border-slate-200 p-6 shrink-0 bg-slate-50">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Add New Question</h3>
          <form onSubmit={addQuestion} className="space-y-3">
            <textarea name="text" value={form.text} onChange={handle} required rows={2}
              placeholder="Question text *"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
            <div className="grid grid-cols-2 gap-2">
              {['a', 'b', 'c', 'd'].map((opt) => (
                <input key={opt} name={`option_${opt}`} value={form[`option_${opt}`]} onChange={handle} required
                  placeholder={`Option ${opt.toUpperCase()} *`}
                  className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              ))}
            </div>
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium text-slate-700">Correct:</label>
              {['A', 'B', 'C', 'D'].map((opt) => (
                <label key={opt} className="flex items-center gap-1 cursor-pointer">
                  <input type="radio" name="correct_option" value={opt} checked={form.correct_option === opt} onChange={handle}
                    className="text-blue-600" />
                  <span className="text-sm font-medium">{opt}</span>
                </label>
              ))}
              <button type="submit" disabled={saving}
                className="ml-auto px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition disabled:opacity-50">
                {saving ? 'Adding...' : '+ Add'}
              </button>
            </div>
          </form>
        </div>
      </div>
      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────
export default function AdminAssessmentsPage() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [modal, setModal] = useState(null);             // null | assessment object (for edit) | {} (for create)
  const [questionPanel, setQuestionPanel] = useState(null); // null | full assessment object
  const [confirmModal, setConfirmModal] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getAssessments();
      setAssessments(res.data.data || []);
    } catch {
      toast.error('Failed to load assessments');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = assessments.filter((a) => {
    const q = search.toLowerCase();
    return (!q || a.title?.toLowerCase().includes(q)) && (!domainFilter || a.domain === domainFilter);
  });

  const openQuestions = async (a) => {
    try {
      const res = await adminService.getAssessment(a.id);
      setQuestionPanel(res.data.data);
    } catch {
      toast.error('Failed to load questions');
    }
  };

  const handleToggle = (a) => {
    setConfirmModal({
      title: `${a.is_active ? 'Deactivate' : 'Activate'} Assessment`,
      message: `${a.is_active ? 'Deactivate' : 'Activate'} "${a.title}"?`,
      danger: a.is_active,
      confirmLabel: a.is_active ? 'Deactivate' : 'Activate',
      onConfirm: async () => {
        await adminService.toggleAssessment(a.id);
        toast.success(`Assessment ${a.is_active ? 'deactivated' : 'activated'}`);
        load();
      },
    });
  };

  const handleDelete = (a) => {
    setConfirmModal({
      title: 'Delete Assessment',
      message: `Delete "${a.title}"? All questions and attempts will be removed.`,
      danger: true,
      confirmLabel: 'Delete',
      onConfirm: async () => {
        await adminService.deleteAssessment(a.id);
        toast.success('Assessment deleted');
        load();
      },
    });
  };

  return (
    <DashboardLayout>
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">📋 Assessments</h1>
          <p className="text-slate-500 text-sm mt-1">{assessments.length} total • {assessments.filter((a) => a.is_active).length} active</p>
        </div>
        <button onClick={() => setModal({})}
          className="shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition">
          + New Assessment
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <input value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by title..."
          className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <select value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Domains</option>
          {DOMAINS.map((d) => <option key={d}>{d}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center py-16">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-slate-500">No assessments found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Title</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Domain</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Questions</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Time</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Status</th>
                  <th className="text-right px-4 py-3 font-semibold text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50 transition">
                    <td className="px-4 py-3 font-medium text-slate-900">{a.title}</td>
                    <td className="px-4 py-3"><Badge text={a.domain} status="info" size="sm" /></td>
                    <td className="px-4 py-3 text-slate-600">{a.question_count}</td>
                    <td className="px-4 py-3 text-slate-500">{a.time_limit ? `${a.time_limit} min` : '—'}</td>
                    <td className="px-4 py-3">
                      <Badge text={a.is_active ? 'Active' : 'Inactive'} status={a.is_active ? 'success' : 'error'} size="sm" />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => openQuestions(a)} title="Manage Questions"
                          className="p-1.5 text-slate-500 hover:text-purple-600 hover:bg-purple-50 rounded transition text-base">📝</button>
                        <button onClick={() => setModal(a)} title="Edit"
                          className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded transition text-base">✏️</button>
                        <button onClick={() => handleToggle(a)} title={a.is_active ? 'Deactivate' : 'Activate'}
                          className="p-1.5 text-slate-500 hover:text-yellow-600 hover:bg-yellow-50 rounded transition text-base">
                          {a.is_active ? '🔒' : '🔓'}
                        </button>
                        <button onClick={() => handleDelete(a)} title="Delete"
                          className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded transition text-base">🗑️</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modal !== null && (
        <AssessmentModal assessment={modal} onClose={() => setModal(null)} onSave={load} />
      )}
      {questionPanel && (
        <QuestionPanel
          assessment={questionPanel}
          onClose={() => setQuestionPanel(null)}
          onUpdated={load}
        />
      )}
      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
}
