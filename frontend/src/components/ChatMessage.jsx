import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message, onFeedbackClick }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="max-w-3xl w-full">
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-slate-100 text-slate-900 rounded-bl-none border border-slate-200'
          }`}
        >
          <div className={`${isUser ? 'text-white' : 'text-slate-900'} text-sm leading-relaxed`}>
            <ReactMarkdown
              components={{
                // Custom markdown rendering
                p: ({ node, ...props }) => (
                  <p className="mb-2 last:mb-0" {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul className="list-disc list-inside mb-2 space-y-1" {...props} />
                ),
                ol: ({ node, ...props }) => (
                  <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />
                ),
                li: ({ node, ...props }) => (
                  <li className="ml-2" {...props} />
                ),
                strong: ({ node, ...props }) => (
                  <strong className="font-bold" {...props} />
                ),
                em: ({ node, ...props }) => (
                  <em className="italic" {...props} />
                ),
                code: ({ node, inline, ...props }) => (
                  inline ? (
                    <code className={`${isUser ? 'bg-blue-700 px-1 rounded' : 'bg-slate-200 px-1 rounded'} font-mono text-xs`} {...props} />
                  ) : (
                    <pre className={`${isUser ? 'bg-blue-700' : 'bg-slate-200'} p-2 rounded mt-2 mb-2 overflow-x-auto`}>
                      <code {...props} />
                    </pre>
                  )
                ),
                h1: ({ node, ...props }) => (
                  <h1 className="text-lg font-bold mb-2 mt-2" {...props} />
                ),
                h2: ({ node, ...props }) => (
                  <h2 className="text-base font-bold mb-2 mt-2" {...props} />
                ),
                h3: ({ node, ...props }) => (
                  <h3 className="text-sm font-bold mb-1 mt-1" {...props} />
                ),
                blockquote: ({ node, ...props }) => (
                  <blockquote className={`border-l-4 ${isUser ? 'border-blue-400' : 'border-slate-400'} pl-3 italic my-2`} {...props} />
                ),
                a: ({ node, ...props }) => (
                  <a className={`underline ${isUser ? 'text-blue-200 hover:text-white' : 'text-blue-600 hover:text-blue-800'}`} {...props} />
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>
        
        {/* Timestamp and Feedback */}
        <div className="flex items-center justify-between mt-2 px-1">
          <p className="text-xs text-slate-500">
            {new Date(message.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
          {!isUser && onFeedbackClick && (
            <button
              onClick={() => onFeedbackClick(message.id)}
              className="text-xs text-slate-500 hover:text-green-600 transition"
              title="Rate this response"
            >
              👍
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
