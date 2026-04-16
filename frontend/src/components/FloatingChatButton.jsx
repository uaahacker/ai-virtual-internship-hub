import React, { useState } from 'react';
import ChatWidget from './ChatWidget';

const FloatingChatButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => {
            setIsOpen(true);
            setIsMinimized(false);
            setUnreadCount(0);
          }}
          className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-full shadow-lg hover:shadow-xl hover:scale-110 transition-all flex items-center justify-center text-2xl z-40 group"
          title="Open Career Guidance Bot"
        >
          💬
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
          <span className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white px-3 py-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap text-sm">
            Career Guidance Bot
          </span>
        </button>
      )}

      {/* Chat Widget */}
      <ChatWidget
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        isMinimized={isMinimized}
        onMinimize={setIsMinimized}
      />
    </>
  );
};

export default FloatingChatButton;
