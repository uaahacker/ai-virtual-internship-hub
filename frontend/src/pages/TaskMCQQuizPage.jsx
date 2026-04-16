import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import { FiCheckCircle, FiArrowRight, FiArrowLeft, FiClock } from 'react-icons/fi';

export default function TaskMCQQuizPage() {
  const { completionId, taskId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchMCQQuestions();
    setStartTime(Date.now());
  }, [user, navigate, taskId]);

  // Timer effect
  useEffect(() => {
    if (!startTime) return;
    const interval = setInterval(() => {
      setTimeElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  const fetchMCQQuestions = async () => {
    try {
      setLoading(true);
      const response = await taskService.getMCQQuestions(taskId);
      if (response.data.success) {
        const qs = response.data.data.questions;
        setQuestions(qs);
        // Initialize answers
        const initialAnswers = {};
        qs.forEach(q => {
          initialAnswers[q.id] = '';
        });
        setAnswers(initialAnswers);
      } else {
        setError(response.data.error?.message || 'Failed to load quiz questions');
      }
    } catch (err) {
      setError('Error loading quiz');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, choice) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: choice
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleGoToQuestion = (index) => {
    setCurrentQuestion(index);
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setError('');

      // Check if all questions are answered
      const unanswered = questions.filter(q => !answers[q.id]);
      if (unanswered.length > 0) {
        setError(`Please answer all ${unanswered.length} question(s) before submitting.`);
        setSubmitting(false);
        return;
      }

      // Format answers for submission
      const formattedAnswers = {};
      questions.forEach(q => {
        formattedAnswers[q.id] = answers[q.id];
      });

      const response = await taskService.submitMCQAnswers(
        completionId,
        formattedAnswers,
        timeElapsed
      );

      if (response.data.success) {
        // Navigate to evaluation results
        const evaluationId = response.data.data.evaluation_id;
        navigate(`/student/tasks/evaluation/${evaluationId}`, {
          state: {
            score: response.data.data.mcq_score,
            correct: response.data.data.correct_answers,
            total: response.data.data.total_questions
          }
        });
      } else {
        setError(response.data.error?.message || 'Failed to submit quiz');
      }
    } catch (err) {
      setError('Error submitting quiz');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const currentQ = questions[currentQuestion];
  const answeredCount = Object.values(answers).filter(a => a).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-8 px-4">
        <div className="text-center">
          <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600">Loading quiz questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Task Quiz</h1>
              <p className="text-gray-600">{answeredCount} of {questions.length} questions answered</p>
            </div>
            <div className="flex items-center gap-3 text-lg font-bold text-gray-900 bg-gray-100 px-4 py-2 rounded-lg">
              <FiClock size={20} />
              {formatTime(timeElapsed)}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Quiz Area */}
          <div className="lg:col-span-3">
            {currentQ && (
              <div className="bg-white rounded-lg border border-gray-200 p-8">
                {/* Question Header */}
                <div className="mb-8">
                  <p className="text-sm font-medium text-blue-600 uppercase">Question {currentQuestion + 1} of {questions.length}</p>
                  <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Question Text */}
                <h2 className="text-xl font-bold text-gray-900 mb-6">{currentQ.question_text}</h2>

                {/* Difficulty Badge */}
                <div className="mb-6">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    currentQ.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                    currentQ.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {currentQ.difficulty}
                  </span>
                </div>

                {/* Answer Options */}
                <div className="space-y-3 mb-8">
                  {['A', 'B', 'C', 'D'].map((option) => {
                    const optionField = `option_${option.toLowerCase()}`;
                    const optionText = currentQ[optionField];
                    const isSelected = answers[currentQ.id] === option;

                    return (
                      <label
                        key={option}
                        className={`block p-4 border-2 rounded-lg cursor-pointer transition ${
                          isSelected
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-gray-200 bg-white hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <input
                            type="radio"
                            name={`question-${currentQ.id}`}
                            value={option}
                            checked={isSelected}
                            onChange={() => handleAnswerChange(currentQ.id, option)}
                            className="mt-1"
                          />
                          <div>
                            <p className="font-bold text-gray-900">{option}</p>
                            <p className="text-gray-700 mt-1">{optionText}</p>
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>

                {/* Navigation Buttons */}
                <div className="flex gap-4">
                  <button
                    onClick={handlePrevious}
                    disabled={currentQuestion === 0}
                    className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <FiArrowLeft size={18} />
                    Previous
                  </button>

                  {currentQuestion < questions.length - 1 ? (
                    <button
                      onClick={handleNext}
                      className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium flex items-center justify-center gap-2"
                    >
                      Next
                      <FiArrowRight size={18} />
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={submitting || answeredCount < questions.length}
                      className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submitting ? 'Submitting...' : 'Submit Quiz'}
                      <FiCheckCircle size={18} />
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Question Navigation Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg border border-gray-200 p-6 sticky top-4">
              <h3 className="font-bold text-gray-900 mb-4">Questions</h3>
              <div className="grid grid-cols-4 lg:grid-cols-3 gap-2">
                {questions.map((q, idx) => (
                  <button
                    key={q.id}
                    onClick={() => handleGoToQuestion(idx)}
                    className={`w-10 h-10 rounded-lg font-bold text-sm transition flex items-center justify-center ${
                      currentQuestion === idx
                        ? 'bg-blue-600 text-white'
                        : answers[q.id]
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-600 border border-gray-200 hover:border-gray-300'
                    }`}
                    title={`Question ${idx + 1}`}
                  >
                    {idx + 1}
                  </button>
                ))}
              </div>

              {/* Quiz Info */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-3">
                  <strong>Progress:</strong> {answeredCount}/{questions.length}
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${(answeredCount / questions.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
