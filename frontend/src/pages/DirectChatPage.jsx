import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import DashboardLayout from '../components/DashboardLayout';
import { useAuth } from '../contexts/AuthContext';
import { directMessageService, profileService } from '../services/endpoints';

export default function DirectChatPage() {
  const { user } = useAuth();
  const role = user?.role;
  const { studentId } = useParams(); // set for Mentor route, undefined for Student

  const [otherUser, setOtherUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef(null);
  const intervalRef = useRef(null);

  // For Student: resolve mentor ID from profile
  const [otherId, setOtherId] = useState(studentId ? Number(studentId) : null);
  const [resolving, setResolving] = useState(!studentId && role === 'Student');

  // Students need to look up their mentor from their profile
  useEffect(() => {
    if (role !== 'Student' || studentId) return;
    setResolving(true);
    profileService.getStudentProfile()
      .then((res) => {
        if (res.data.success) {
          const profile = res.data.data;
          const mentorId = profile.mentor_assigned;
          if (mentorId) {
            setOtherId(Number(mentorId));
          } else {
            toast.error('No mentor assigned yet.');
          }
        }
      })
      .catch(() => toast.error('Could not load your profile.'))
      .finally(() => setResolving(false));
  }, [role, studentId]);

  const loadMessages = useCallback(async () => {
    if (!otherId) return;
    try {
      const res = await directMessageService.getConversation(otherId);
      if (res.data.success) {
        setMessages(res.data.data || []);
        if (!otherUser && res.data.other_user) {
          setOtherUser(res.data.other_user);
        }
      }
    } catch {
      // silent polling failure
    } finally {
      setLoading(false);
    }
  }, [otherId, otherUser]);

  // Initial load + polling every 5s
  useEffect(() => {
    if (!otherId) return;
    setLoading(true);
    loadMessages();
    intervalRef.current = setInterval(loadMessages, 5000);
    return () => clearInterval(intervalRef.current);
  }, [otherId, loadMessages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    const content = input.trim();
    if (!content || !otherId) return;
    setSending(true);
    try {
      const res = await directMessageService.send(otherId, content);
      if (res.data.success) {
        setMessages((prev) => [...prev, res.data.data]);
        setInput('');
      } else {
        toast.error(res.data.error || 'Failed to send message.');
      }
    } catch {
      toast.error('Error sending message.');
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (resolving) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64 text-gray-400">Looking up your mentor...</div>
      </DashboardLayout>
    );
  }

  if (!otherId) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-64 gap-2">
          <p className="text-2xl">👤</p>
          <p className="text-gray-500 font-medium">No mentor assigned yet.</p>
          <p className="text-sm text-gray-400">You'll be able to chat once a mentor accepts you.</p>
        </div>
      </DashboardLayout>
    );
  }

  const displayName = otherUser?.name || (role === 'Student' ? 'Your Mentor' : 'Student');
  const displayRole = otherUser?.role || '';

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto px-4 py-4 flex flex-col flex-1 min-h-0 h-full">
        {/* Header */}
        <div className="bg-white rounded-t-xl border border-b-0 border-gray-200 px-5 py-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-lg">
            {displayName.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-800">{displayName}</p>
            {displayRole && <p className="text-xs text-gray-400">{displayRole}</p>}
          </div>
          <span className="ml-auto flex items-center gap-1 text-xs text-green-500 font-medium">
            <span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span> Live
          </span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-gray-50 border-x border-gray-200 px-4 py-4 space-y-3">
          {loading ? (
            <div className="text-center text-gray-400 py-8">Loading messages...</div>
          ) : messages.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <p className="text-3xl mb-2">💬</p>
              <p>No messages yet. Say hello!</p>
            </div>
          ) : (
            messages.map((msg) => {
              const isMine = msg.is_mine;
              return (
                <div key={msg.id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      isMine
                        ? 'bg-indigo-600 text-white rounded-br-none'
                        : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className={`text-xs mt-1 ${isMine ? 'text-indigo-200' : 'text-gray-400'} text-right`}>
                      {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              );
            })
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="bg-white rounded-b-xl border border-t-0 border-gray-200 px-4 py-3 flex items-end gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message... (Enter to send)"
            rows={1}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400 max-h-28 overflow-y-auto"
            style={{ lineHeight: '1.5' }}
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white rounded-xl px-4 py-2.5 text-sm font-medium transition-colors flex-shrink-0"
          >
            {sending ? '...' : '➤'}
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}
