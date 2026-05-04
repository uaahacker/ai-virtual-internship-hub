import { useEffect } from 'react';

/**
 * Reusable confirmation modal — replaces window.confirm().
 *
 * Usage:
 *   const [confirm, setConfirm] = useState(null);
 *   // trigger:
 *   setConfirm({ title: 'Delete item?', message: 'This cannot be undone.', onConfirm: () => doDelete() });
 *   // render:
 *   <ConfirmModal config={confirm} onClose={() => setConfirm(null)} />
 */
export default function ConfirmModal({ config, onClose }) {
  // Close on Escape
  useEffect(() => {
    if (!config) return;
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [config, onClose]);

  if (!config) return null;

  const { title, message, confirmLabel = 'Confirm', cancelLabel = 'Cancel', danger = true, loading = false } = config;

  const handleConfirm = () => {
    config.onConfirm?.();
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-sm mx-auto overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Icon strip */}
        <div className={`h-1.5 w-full ${danger ? 'bg-red-500' : 'bg-blue-500'}`} />

        <div className="p-6">
          {/* Title */}
          <div className="flex items-start gap-3 mb-3">
            <div className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-lg ${danger ? 'bg-red-100' : 'bg-blue-100'}`}>
              {danger ? '⚠️' : 'ℹ️'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-base leading-snug">{title}</h3>
              {message && <p className="text-sm text-gray-500 mt-1 leading-relaxed">{message}</p>}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-5 justify-end">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
            >
              {cancelLabel}
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading}
              className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2 ${
                danger ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading && (
                <span className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              )}
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Inline progress input modal — replaces window.prompt() for numeric input.
 */
export function ProgressModal({ config, onClose }) {
  if (!config) return null;
  const { value, onChange, onConfirm, label = 'Progress (0–100)' } = config;

  const handleConfirm = () => {
    onConfirm?.();
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-xs mx-auto overflow-hidden">
        <div className="h-1.5 w-full bg-blue-500" />
        <div className="p-6">
          <h3 className="font-semibold text-gray-900 text-base mb-4">Update Progress</h3>
          <label className="block text-sm text-gray-600 mb-1">{label}</label>
          <input
            type="number"
            min={0}
            max={100}
            value={value}
            onChange={(e) => onChange(Math.min(100, Math.max(0, parseInt(e.target.value) || 0)))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            autoFocus
          />
          <div className="mt-3 bg-gray-100 rounded-full h-2">
            <div className="h-2 rounded-full bg-blue-500 transition-all" style={{ width: `${value}%` }} />
          </div>
          <div className="flex gap-3 mt-5 justify-end">
            <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
              Cancel
            </button>
            <button onClick={handleConfirm} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              Update
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
