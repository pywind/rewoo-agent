import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const StreamingChat = ({ content, isComplete = false, isUserMessage = false }) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (isComplete) {
      setDisplayedContent(content);
      return;
    }

    // Reset when content changes
    if (content !== displayedContent) {
      setCurrentIndex(0);
      setDisplayedContent('');
    }
  }, [content, isComplete]);

  useEffect(() => {
    if (isComplete || !content) return;

    const timer = setInterval(() => {
      if (currentIndex < content.length) {
        setDisplayedContent(content.slice(0, currentIndex + 1));
        setCurrentIndex(prev => prev + 1);
      } else {
        clearInterval(timer);
      }
    }, 20); // Adjust speed as needed

    return () => clearInterval(timer);
  }, [content, currentIndex, isComplete]);

  // For real-time streaming, we want to show content immediately
  const contentToShow = isComplete ? content : content;

  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom components for better styling
          h1: ({children}) => <h1 className={`text-2xl font-bold mb-4 ${isUserMessage ? 'text-white' : 'text-gray-900'}`}>{children}</h1>,
          h2: ({children}) => <h2 className={`text-xl font-bold mb-3 ${isUserMessage ? 'text-white' : 'text-gray-900'}`}>{children}</h2>,
          h3: ({children}) => <h3 className={`text-lg font-bold mb-2 ${isUserMessage ? 'text-white' : 'text-gray-900'}`}>{children}</h3>,
          p: ({children}) => <p className={`mb-3 leading-relaxed ${isUserMessage ? 'text-white' : ''}`}>{children}</p>,
          ul: ({children}) => <ul className="list-disc list-inside mb-3 ml-4">{children}</ul>,
          ol: ({children}) => <ol className="list-decimal list-inside mb-3 ml-4">{children}</ol>,
          li: ({children}) => <li className="mb-1">{children}</li>,
          code: ({node, inline, className, children, ...props}) => {
            if (inline) {
              return (
                <code 
                  className={`px-2 py-1 rounded text-sm font-mono ${
                    isUserMessage 
                      ? 'bg-blue-400 bg-opacity-30 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`} 
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <div className={`rounded-lg mb-3 overflow-x-auto ${
                isUserMessage ? 'bg-blue-400 bg-opacity-30' : 'bg-gray-100'
              }`}>
                <code 
                  className={`block p-4 text-sm font-mono ${
                    isUserMessage ? 'text-white' : 'text-gray-800'
                  }`} 
                  {...props}
                >
                  {children}
                </code>
              </div>
            );
          },
          pre: ({children}) => <div className="mb-3">{children}</div>,
          blockquote: ({children}) => (
            <blockquote className={`border-l-4 pl-4 italic mb-3 ${
              isUserMessage 
                ? 'border-blue-300 text-blue-100' 
                : 'border-blue-500 text-gray-600'
            }`}>
              {children}
            </blockquote>
          ),
          strong: ({children}) => <strong className="font-bold">{children}</strong>,
          em: ({children}) => <em className="italic">{children}</em>,
          a: ({children, href}) => (
            <a 
              href={href} 
              className={`underline ${
                isUserMessage 
                  ? 'text-blue-100 hover:text-white' 
                  : 'text-blue-600 hover:text-blue-800'
              }`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          table: ({children}) => (
            <div className="overflow-x-auto mb-3">
              <table className="min-w-full border border-gray-300">
                {children}
              </table>
            </div>
          ),
          thead: ({children}) => (
            <thead className="bg-gray-50">
              {children}
            </thead>
          ),
          tbody: ({children}) => (
            <tbody className="divide-y divide-gray-200">
              {children}
            </tbody>
          ),
          tr: ({children}) => (
            <tr className="hover:bg-gray-50">
              {children}
            </tr>
          ),
          th: ({children}) => (
            <th className={`px-4 py-2 text-left font-medium border-b ${
              isUserMessage 
                ? 'text-white border-blue-300' 
                : 'text-gray-900 border-gray-300'
            }`}>
              {children}
            </th>
          ),
          td: ({children}) => (
            <td className={`px-4 py-2 border-b ${
              isUserMessage 
                ? 'text-blue-100 border-blue-300' 
                : 'text-gray-800 border-gray-200'
            }`}>
              {children}
            </td>
          )
        }}
      >
        {contentToShow}
      </ReactMarkdown>
      {!isComplete && contentToShow && (
        <span className="typing-indicator text-gray-400"></span>
      )}
    </div>
  );
};

export default StreamingChat;