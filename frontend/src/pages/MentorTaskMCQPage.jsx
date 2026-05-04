import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import DashboardLayout from '../components/DashboardLayout';
import { taskService } from '../services/endpoints';
import ConfirmModal from '../components/ConfirmModal';

const DIFFICULTY_OPTIONS = ['Easy', 'Medium', 'Hard'];
const ANSWER_OPTIONS = ['A', 'B', 'C', 'D'];

const EMPTY_FORM = {
  question_text: '',
  option_a: '',
  option_b: '',
  option_c: '',
  option_d: '',
  correct_answer: 'A',
  difficulty: 'Medium',
  explanation: '',
  order: 0,
};

export default function MentorTaskMCQPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();

  const [taskTitle, setTaskTitle] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [confirmModal, setConfirmModal] = useState(null);

  const loadQuestions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await taskService.getMentorTaskMCQ(taskId);
      if (res.data.success) {
        setTaskTitle(res.data.data.task_title);
        setQuestions(res.data.data.questions || []);
      } else {
        toast.error(res.data.error || 'Failed to load questions.');
        navigate('/mentor/tasks');
      }
    } catch {
      toast.error('Failed to load questions.');
      navigate('/mentor/tasks');
    } finally {
      setLoading(false);
    }
  }, [taskId, navigate]);

  useEffect(() => { loadQuestions(); }, [loadQuestions]);

  const openCreate = () => {
    setEditingId(null);
    setForm({ ...EMPTY_FORM, order: questions.length });
    setShowForm(true);
  };

  const openEdit = (q) => {
    setEditingId(q.id);
    setForm({
      question_text: q.question_text,
      option_a: q.option_a,
      option_b: q.option_b,
      option_c: q.option_c,
      option_d: q.option_d,
      correct_answer: q.correct_answer,
      difficulty: q.difficulty,
      explanation: q.explanation || '',
      order: q.order,
    });
    setShowForm(true);
  };

  const handleFormChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const required = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'];
    for (const f of required) {
      if (!form[f]?.trim()) {
        toast.error(`${f.replace(/_/g, ' ')} is required.`);
        return;
      }
    }
    setSubmitting(true);
    try {
      let res;
      if (editingId) {
        res = await taskService.updateMentorTaskMCQ(taskId, editingId, form);
      } else {
        res = await taskService.createMentorTaskMCQ(taskId, form);
      }
      if (res.data.success) {
        toast.success(editingId ? 'Question updated!' : 'Question added!');
        setShowForm(false);
        setEditingId(null);
        loadQuestions();
      } else {
        toast.error(res.data.error || 'Failed to save question.');
      }
    } catch {
      toast.error('Error saving question.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    setConfirmModal({
      title: 'Delete question?',
      message: 'This MCQ question will be permanently removed.',
      confirmLabel: 'Delete',
      danger: true,
      onConfirm: async () => {
        setDeletingId(id);
        try {
          const res = await taskService.deleteMentorTaskMCQ(taskId, id);
          if (res.data.success) {
            toast.success('Question deleted.');
            setQuestions((prev) => prev.filter((q) => q.id !== id));
          } else {
            toast.error(res.data.error || 'Delete failed.');
          }
        } catch {
          toast.error('Delete failed.');
        } finally {
          setDeletingId(null);
        }
      },
    });
  };

  const difficultyColor = (d) => ({
    Easy: 'bg-green-100 text-green-700',
    Medium: 'bg-yellow-100 text-yellow-700',
    Hard: 'bg-red-100 text-red-700',
  }[d] || 'bg-gray-100 text-gray-600');

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <button
              onClick={() => navigate('/mentor/tasks')}
              className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1 mb-2"
            >
              ← Back to Tasks
            </button>
            <h1 className="text-2xl font-bold text-gray-800">Quiz Questions</h1>
            {taskTitle && (
              <p className="text-sm text-gray-500 mt-0.5">
                Task: <span className="font-medium text-gray-700">{taskTitle}</span>
              </p>
            )}
          </div>
          {!showForm && (
            <button
              onClick={openCreate}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              + Add Question
            </button>
          )}
        </div>

        {/* Empty state */}
        {!loading && questions.length === 0 && !showForm && (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center mb-6">
            <p className="text-4xl mb-3">📝</p>
            <p className="text-lg font-semibold text-gray-800 mb-2">No quiz questions yet</p>
            <p className="text-sm text-gray-500 mb-6">
              Add MCQ questions that students will answer after completing this task.
            </p>
            <button
              onClick={openCreate}
              className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
            >
              + Add First Question
            </button>
          </div>
        )}

        {/* Question Form */}
        {showForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-base font-semibold text-gray-700 mb-4">
              {editingId ? 'Edit Question' : 'New Question'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Question text */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Question</label>
                <textarea
                  value={form.question_text}
                  onChange={(e) => handleFormChange('question_text', e.target.value)}
                  placeholder="Enter your question..."
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
                />
              </div>

              {/* Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {['a', 'b', 'c', 'd'].map((letter) => (
                  <div key={letter}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Option {letter.toUpperCase()}
                    </label>
                    <input
                      type="text"
                      value={form[`option_${letter}`]}
                      onChange={(e) => handleFormChange(`option_${letter}`, e.target.value)}
                      placeholder={`Option ${letter.toUpperCase()}...`}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                    />
                  </div>
                ))}
              </div>

              {/* Correct answer + difficulty */}
              <div className="flex gap-4 flex-wrap">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Correct Answer</label>
                  <select
                    value={form.correct_answer}
                    onChange={(e) => handleFormChange('correct_answer', e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  >
                    {ANSWER_OPTIONS.map((o) => (
                      <option key={o} value={o}>Option {o}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                  <select
                    value={form.difficulty}
                    onChange={(e) => handleFormChange('difficulty', e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  >
                    {DIFFICULTY_OPTIONS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
                  <input
                    type="number"
                    min={0}
                    value={form.order}
                    onChange={(e) => handleFormChange('order', Number(e.target.value))}
                    className="w-20 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  />
                </div>
              </div>

              {/* Explanation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Explanation <span className="text-gray-400 font-normal">(optional)</span>
                </label>
                <textarea
                  value={form.explanation}
                  onChange={(e) => handleFormChange('explanation', e.target.value)}
                  placeholder="Explain why this is the correct answer..."
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
                >
                  {submitting ? 'Saving...' : editingId ? 'Update' : 'Add Question'}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowForm(false); setEditingId(null); }}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium px-5 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Question List */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading questions...</div>
        ) : (
          <div className="space-y-3">
            {questions.map((q, idx) => (
              <div key={q.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center flex-shrink-0">
                        {idx + 1}
                      </span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${difficultyColor(q.difficulty)}`}>
                        {q.difficulty}
                      </span>
                      <span className="text-xs text-gray-400">Correct: <span className="font-semibold text-green-600">Option {q.correct_answer}</span></span>
                    </div>
                    <p className="text-sm font-medium text-gray-800 mb-3">{q.question_text}</p>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                      {['a', 'b', 'c', 'd'].map((letter) => (
                        <div key={letter} className={`flex items-start gap-1.5 text-xs ${q.correct_answer === letter.toUpperCase() ? 'text-green-700 font-semibold' : 'text-gray-600'}`}>
                          <span className={`w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold mt-0.5 ${q.correct_answer === letter.toUpperCase() ? 'bg-green-100' : 'bg-gray-100 text-gray-500'}`}>
                            {letter.toUpperCase()}
                          </span>
                          <span>{q[`option_${letter}`]}</span>
                        </div>
                      ))}
                    </div>
                    {q.explanation && (
                      <p className="mt-3 text-xs text-gray-500 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
                        💡 {q.explanation}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => openEdit(q)}
                      className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(q.id)}
                      disabled={deletingId === q.id}
                      className="px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 disabled:opacity-50 transition"
                    >
                      {deletingId === q.id ? '...' : 'Delete'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bottom add button if questions exist */}
        {!loading && questions.length > 0 && !showForm && (
          <div className="mt-4 text-center">
            <button
              onClick={openCreate}
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              + Add Another Question
            </button>
          </div>
        )}
      </div>
      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
}
