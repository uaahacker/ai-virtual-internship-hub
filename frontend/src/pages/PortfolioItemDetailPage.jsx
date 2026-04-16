import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function PortfolioItemDetailPage() {
  const { itemId } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    loadItem();
  }, [itemId]);

  const loadItem = async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await api.get(`/tasks/portfolio-items/${itemId}/`);
      if (res.data.success) {
        setItem(res.data.data);
        setFormData({
          is_featured: res.data.data.is_featured || false,
          display_order: res.data.data.display_order || 0,
        });
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load portfolio item');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await api.put(
        `/tasks/portfolio-items/${itemId}/update/`,
        formData
      );
      if (res.data.success) {
        setItem(res.data.data);
        setEditMode(false);
        alert('Portfolio item updated successfully');
      }
    } catch (err) {
      alert(err.response?.data?.errors || 'Failed to update portfolio item');
    }
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : parseInt(value),
    }));
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading portfolio item...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 mb-4">{error}</p>
            <button
              onClick={() => navigate('/student/portfolio')}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Back to Portfolio
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/student/portfolio')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-4"
          >
            ← Back to Portfolio
          </button>
          <div className="bg-gray-100 rounded-lg p-8 text-center">
            <p className="text-gray-600">Portfolio item not found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 print:bg-white">
      {/* Header */}
      <div className="bg-white shadow print:shadow-none print:border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-between items-start mb-4">
            <button
              onClick={() => navigate('/student/portfolio')}
              className="text-blue-600 hover:text-blue-800 font-medium print:hidden"
            >
              ← Back to Portfolio
            </button>
            <div className="flex gap-2 print:hidden">
              <button
                onClick={() => setEditMode(!editMode)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                {editMode ? 'Cancel' : 'Edit'}
              </button>
              <button
                onClick={handlePrint}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
              >
                Print
              </button>
            </div>
          </div>

          <div>
            <h1 className="text-3xl font-bold text-gray-900">{item.task_title}</h1>
            <p className="mt-1 text-gray-600">{item.task_type}</p>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mt-4">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
              {item.task_domain}
            </span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
              {item.task_difficulty}
            </span>
            {item.is_featured && (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">
                ⭐ Featured
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Edit Mode */}
      {editMode && (
        <div className="bg-white border-b shadow">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="is_featured"
                  name="is_featured"
                  checked={formData.is_featured}
                  onChange={handleFormChange}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <label htmlFor="is_featured" className="text-sm text-gray-700">
                  Feature this item on portfolio
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Display Order
                </label>
                <input
                  type="number"
                  name="display_order"
                  value={formData.display_order}
                  onChange={handleFormChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                />
              </div>

              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Save Changes
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Scores Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Scores</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* MCQ Score */}
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">MCQ Score</p>
              <div className="flex items-end gap-3">
                <span className="text-3xl font-bold text-blue-600">{item.mcq_score}</span>
                <span className="text-gray-500 mb-1">/100</span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${item.mcq_score}%` }}
                ></div>
              </div>
            </div>

            {/* Mentor Score */}
            {item.mentor_score !== null && (
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">Mentor Score</p>
                <div className="flex items-end gap-3">
                  <span className="text-3xl font-bold text-purple-600">{item.mentor_score}</span>
                  <span className="text-gray-500 mb-1">/100</span>
                </div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${item.mentor_score}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Final Score */}
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">Final Score</p>
              <div className="flex items-end gap-3">
                <span className="text-3xl font-bold text-green-600">{item.final_score}</span>
                <span className="text-gray-500 mb-1">/100</span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${item.final_score}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Dates Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Timeline</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Completed on:</span>
              <span className="font-semibold text-gray-900">
                {new Date(item.completion_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Evaluated on:</span>
              <span className="font-semibold text-gray-900">
                {new Date(item.evaluation_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
          </div>
        </div>

        {/* Project Summary */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Project Summary</h2>
          <p className="text-gray-700 leading-relaxed">{item.project_summary}</p>
        </div>

        {/* Skills Demonstrated */}
        {item.skills_demonstrated && item.skills_demonstrated.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Skills Demonstrated</h2>
            <div className="flex flex-wrap gap-2">
              {item.skills_demonstrated.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-2 bg-purple-100 text-purple-800 rounded-lg text-sm font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Student Reflection */}
        {item.student_reflection && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">My Reflection</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {item.student_reflection}
            </p>
          </div>
        )}

        {/* Mentor Feedback */}
        {item.mentor_feedback_summary && (
          <div className="bg-blue-50 rounded-lg border border-blue-200 p-6 mb-6">
            <h2 className="text-lg font-bold text-blue-900 mb-4">📝 Mentor Feedback</h2>
            <p className="text-blue-800 leading-relaxed">{item.mentor_feedback_summary}</p>
          </div>
        )}

        {/* Strengths */}
        {item.strengths_summary && (
          <div className="bg-green-50 rounded-lg border border-green-200 p-6 mb-6">
            <h2 className="text-lg font-bold text-green-900 mb-4">💪 Strengths</h2>
            <div className="text-green-800 whitespace-pre-wrap">{item.strengths_summary}</div>
          </div>
        )}
      </div>

      {/* Print Styles */}
      <style>{`
        @media print {
          body {
            background: white;
          }
          .print\\:hidden,
          [class*="print:hidden"] {
            display: none !important;
          }
          .print\\:bg-white {
            background-color: white !important;
          }
          .print\\:shadow-none {
            box-shadow: none !important;
          }
          .print\\:border-b {
            border-bottom: 1px solid #e5e7eb !important;
          }
          .print\\:page-break-inside-avoid {
            page-break-inside: avoid !important;
          }
        }
      `}</style>
    </div>
  );
}
