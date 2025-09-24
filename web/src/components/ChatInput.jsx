import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Mic, Paperclip, Sparkles } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation.js';

const ChatInput = ({
  inputMessage,
  setInputMessage,
  onSendMessage,
  isStreaming,
  disabled = false
}) => {
  const t = useTranslation();
  const inputRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);
  const [inputHeight, setInputHeight] = useState('auto');

  // Debug translations
  const placeholderText = t('input_placeholder') || 'Ask me anything...';
  const yourMessageText = t('your_message') || 'Type your message';
  
  console.log('Translation debug:', {
    placeholderText,
    yourMessageText,
    tFunction: typeof t,
    rawTranslation: t('input_placeholder')
  });

  // Auto-resize textarea
  const adjustTextareaHeight = () => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      const scrollHeight = inputRef.current.scrollHeight;
      const maxHeight = 120; // Maximum height in pixels
      const newHeight = Math.min(scrollHeight, maxHeight);
      inputRef.current.style.height = `${newHeight}px`;
      setInputHeight(`${newHeight}px`);
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputMessage]);

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isStreaming && inputMessage.trim()) {
      e.preventDefault();
      onSendMessage();
    }
  };

  const handleSendClick = () => {
    if (!isStreaming && inputMessage.trim()) {
      onSendMessage();
    }
  };

  const isInputEmpty = !inputMessage.trim();

  return (
    <div className="bg-gradient-to-b from-white/90 to-white backdrop-blur-xl border-t border-gray-200/50 p-4 sticky bottom-0">
      <div className="max-w-4xl mx-auto">
        {/* Main Input Container */}
        <div className={`
          relative bg-white/80 backdrop-blur-md border-2 rounded-2xl shadow-lg 
          transition-all duration-300 ease-in-out
          ${isFocused 
            ? 'border-blue-500 shadow-blue-500/20 shadow-xl' 
            : 'border-gray-200 hover:border-gray-300 hover:shadow-xl'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}>
          {/* Input Area */}
          <div className="flex items-end p-4 space-x-3">
            {/* Attachment Button */}
            <button
              className={`
                p-2 rounded-xl transition-all duration-200 flex-shrink-0
                ${disabled 
                  ? 'text-gray-300 cursor-not-allowed' 
                  : 'text-gray-500 hover:text-blue-600 hover:bg-blue-50 active:scale-95'
                }
              `}
              disabled={disabled}
              title={t('attach_file') || 'Attach file'}
            >
              <Paperclip size={20} />
            </button>

            {/* Text Input */}
            <div className="flex-1 relative">
              {/* Floating Label */}
              <label
                className={`
                  absolute left-0 transition-all duration-200 pointer-events-none
                  ${isFocused || inputMessage
                    ? '-top-2 text-xs text-blue-600 font-medium'
                    : 'top-3 text-gray-500 text-base'
                  }
                `}
              >
                {isFocused || inputMessage ? yourMessageText : ''}
              </label>

              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder={!isFocused ? placeholderText : ''}
                className={`
                  w-full resize-none border-0 bg-transparent text-gray-800 
                  placeholder-gray-400 focus:outline-none font-medium text-base
                  leading-relaxed transition-all duration-200
                  ${isFocused || inputMessage ? 'pt-4' : 'pt-3'}
                  pb-1 min-h-[24px]
                `}
                rows={1}
                disabled={disabled || isStreaming}
                style={{ height: inputHeight }}
                autoFocus
              />

              {/* Character count or AI indicator */}
              {inputMessage && (
                <div className="flex justify-between items-center mt-1">
                  <span className="text-xs text-gray-400">
                    {inputMessage.length}/2000
                  </span>
                </div>
              )}
            </div>

            {/* Voice Input Button */}
            <button
              className={`
                p-2 rounded-xl transition-all duration-200 flex-shrink-0
                ${disabled 
                  ? 'text-gray-300 cursor-not-allowed' 
                  : 'text-gray-500 hover:text-blue-600 hover:bg-blue-50 active:scale-95'
                }
              `}
              disabled={disabled}
              title={t('voice_input') || 'Voice input'}
            >
              <Mic size={20} />
            </button>

            {/* Send Button */}
            <button
              onClick={handleSendClick}
              disabled={isInputEmpty || isStreaming || disabled}
              className={`
                relative overflow-hidden rounded-xl p-3 flex-shrink-0
                transition-all duration-300 ease-in-out
                ${isInputEmpty || isStreaming || disabled
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95'
                }
              `}
            >
              {/* Button background animation */}
              {!isInputEmpty && !disabled && (
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-500 opacity-0 hover:opacity-100 transition-opacity duration-300" />
              )}
              
              {/* Button content */}
              <div className="relative z-10 flex items-center">
                {isStreaming ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <Send size={20} />
                )}
              </div>

              {/* Ripple effect */}
              {!isInputEmpty && !disabled && (
                <div className="absolute inset-0 rounded-xl bg-white/20 transform scale-0 group-active:scale-100 transition-transform duration-200" />
              )}
            </button>
          </div>

          {/* Quick Actions Bar (shown when focused) */}
          {isFocused && !disabled && (
            <div className="px-4 pb-3 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <span>💡 Tip: Press Enter to send, Shift+Enter for new line</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="flex items-center space-x-1 text-xs text-gray-400">
                    <Sparkles size={12} className="text-blue-500" />
                    <span>AI-powered response</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Status indicator when streaming */}
        {isStreaming && (
          <div className="flex items-center justify-center mt-3 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="font-medium">{t('ai_thinking') || 'AI is thinking...'}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInput;
