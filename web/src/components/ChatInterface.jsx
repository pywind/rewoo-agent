import React, { useState, useRef, useEffect } from 'react';
import { Bot, User, Loader2 } from 'lucide-react';
import StreamingChat from './StreamingChat.jsx';
import TaskStatus from './TaskStatus.jsx';
import ExampleQueries from './ExampleQueries.jsx';
import ProgressBar from './ProgressBar.jsx';
import LanguageSelector from './LanguageSelector.jsx';
import ChatInput from './ChatInput.jsx';
import { API_ENDPOINTS } from '../config/api.js';
import { useTranslation } from '../hooks/useTranslation.js';

function ChatInterface() {
  const t = useTranslation();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [currentTaskStatus, setCurrentTaskStatus] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isStreaming) return;

    const trimmedMessage = inputMessage.trim();
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: trimmedMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsStreaming(true);
    setCurrentStreamingMessage('');
    setCurrentTaskStatus({ status: 'starting', message: t('initializing_task') });

    try {
      const response = await fetch(API_ENDPOINTS.EXECUTE_STREAM, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: trimmedMessage,
          task_type: 'research',
          priority: 'medium',
          streaming: true
        })
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        // Handle specific status codes
        if (response.status === 422) {
          errorMessage = t('validation_error');
        } else if (response.status === 500) {
          errorMessage = t('server_error');
        } else if (response.status === 404) {
          errorMessage = t('not_found_error');
        }
        
        // Try to get additional error details from response body
        try {
          const errorData = await response.text();
          if (errorData) {
            errorMessage += `. Details: ${errorData}`;
          }
        } catch (parseError) {
          // Ignore parsing errors, use the basic error message
        }
        
        throw new Error(errorMessage);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';
      let hasError = false;

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'task_started') {
                setCurrentTaskStatus({ status: 'running', message: t('task_started') });
              } else if (data.type === 'task_status') {
                const statusData = data.data || {};
                setCurrentTaskStatus({ 
                  status: statusData.status || 'running', 
                  message: statusData.message || t('processing'), 
                  progress: statusData.progress
                });
              } else if (data.type === 'planning_update') {
                const planningData = data.data || {};
                if (planningData.type === 'status') {
                  const statusData = planningData.data || {};
                  setCurrentTaskStatus({ 
                    status: 'planning', 
                    message: statusData.message || t('planning'), 
                    progress: statusData.progress || 0
                  });
                } else {
                  // Handle direct planning_update data structure
                  setCurrentTaskStatus({ 
                    status: 'planning', 
                    message: planningData.message || t('planning'), 
                    progress: planningData.progress || 0
                  });
                }
              } else if (data.type === 'execution_update') {
                const execData = data.data?.data || {};
                if (execData.type === 'step_started') {
                  const stepData = execData.data || {};
                  setCurrentTaskStatus({ 
                    status: 'running', 
                    message: `Step ${stepData.step_number}: ${stepData.description}` 
                  });
                } else if (execData.type === 'step_progress') {
                  const stepData = execData.data || {};
                  const toolUpdate = stepData.tool_update || {};
                  if (toolUpdate.type === 'status') {
                    const toolData = toolUpdate.data || {};
                    setCurrentTaskStatus({ 
                      status: 'running', 
                      message: toolData.message || t('processing'), 
                      progress: toolData.progress 
                    });
                  }
                } else if (execData.type === 'step_completed') {
                  const stepData = execData.data || {};
                  if (stepData.result) {
                    fullResponse += stepData.result + '\n\n';
                    setCurrentStreamingMessage(fullResponse);
                  }
                } else if (execData.type === 'execution_completed') {
                  setCurrentTaskStatus({ status: 'completed', message: t('execution_completed') });
                }
              } else if (data.type === 'task_completed') {
                const result = data.data?.result || '';
                if (result) {
                  fullResponse = result;
                  setCurrentStreamingMessage(result);
                }
                setCurrentTaskStatus({ status: 'completed', message: t('task_completed') });
              } else if (data.type === 'task_failed') {
                setCurrentTaskStatus({ status: 'failed', message: t('task_failed') });
              } else if (data.type === 'error') {
                // Handle backend errors (like JSON serialization errors)
                const errorData = data.data || {};
                const errorMessage = errorData.error || 'An unknown error occurred';
                console.error('Backend error:', errorMessage);
                
                // Set error flag
                hasError = true;
                
                // Set error status and add error message to chat
                setCurrentTaskStatus({ status: 'failed', message: `${t('error')}: ${errorMessage}` });
                
                // Add error message to chat immediately
                const errorChatMessage = {
                  id: Date.now() + 1,
                  type: 'bot',
                  content: `❌ ${t('error')}: ${errorMessage}`,
                  timestamp: new Date(),
                  isError: true,
                  isComplete: true
                };
                setMessages(prev => [...prev, errorChatMessage]);
                
                // Break out of the streaming loop
                reader.cancel();
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
              // Only re-throw if it's not a JSON parsing error and not our custom error
              if (e.message !== 'Unexpected end of JSON input' && !e.message.includes('An internal error has occurred')) {
                throw e;
              }
            }
          }
        }
      }

      // Add the final bot message only if no error occurred
      if (!hasError && (fullResponse || currentStreamingMessage)) {
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: fullResponse || currentStreamingMessage,
          timestamp: new Date(),
          isComplete: true
        };
        setMessages(prev => [...prev, botMessage]);
      }

    } catch (error) {
      console.error('Error:', error);
      
      // More user-friendly error message
      let displayError = error.message;
      if (error.message.includes('JSON serializable')) {
        displayError = t('data_formatting_error');
      } else if (error.message.includes('422')) {
        displayError = t('try_rephrasing');
      } else if (error.message.includes('Failed to fetch')) {
        displayError = t('connection_error');
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `❌ ${t('error')}: ${displayError}\n**${t('technical_details')}**: ${error.message}`,
        timestamp: new Date(),
        isError: true,
        isComplete: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsStreaming(false);
      setCurrentStreamingMessage('');
      setCurrentTaskStatus(null);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200/50 p-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <div className="mr-3 p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg">
                <Bot className="text-white" size={24} />
              </div>
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {t('header_title')}
              </span>
            </h1>
            <p className="text-sm text-gray-600 mt-1 ml-12">{t('header_subtitle')}</p>
          </div>
          <div className="flex items-center space-x-3">
            <LanguageSelector />
            <div className="h-8 w-px bg-gray-300"></div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-4xl mx-auto h-full">
          <div className="h-full overflow-y-auto custom-scrollbar p-4 space-y-4">
            {messages.length === 0 && !isStreaming && (
              <div className="text-center mt-12 reveal">
                <div className="floating mb-8">
                  <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-2xl flex items-center justify-center">
                    <Bot size={40} className="text-white" />
                  </div>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2 gradient-text">
                  {t('welcome')}
                </h2>
                <p className="text-gray-600 text-lg mb-8 max-w-2xl mx-auto leading-relaxed">
                  {t('ask_anything')}
                </p>
                <div className="max-w-4xl mx-auto">
                  <ExampleQueries onSelectQuery={setInputMessage} />
                </div>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} reveal`}
              >
                <div className={`flex w-full ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-end`}>
                  <div className={`flex-shrink-0 ${message.type === 'user' ? 'ml-3' : 'mr-3'}`}> 
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg hover-scale ${
                      message.type === 'user' 
                        ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-blue-500/25' 
                        : message.isError 
                        ? 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-red-500/25'
                        : 'bg-gradient-to-br from-gray-600 to-gray-800 text-white shadow-gray-600/25'
                    }`}>
                      {message.type === 'user' ? <User size={18} /> : <Bot size={18} />}
                    </div>
                  </div>
                  <div
                    className={`rounded-2xl px-5 py-4 card-modern ${
                      message.type === 'user' 
                        ? 'max-w-2xl bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-glow-blue border-0' 
                        : message.isError
                        ? 'max-w-4xl bg-gradient-to-br from-red-50 to-red-100/50 text-red-800 border border-red-200/50 shadow-glow'
                        : 'max-w-4xl bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200/50 shadow-glow hover:shadow-glow-blue'
                    }`}
                  >
                    <div className={`${message.type === 'user' ? 'text-white' : 'text-gray-800'} whitespace-pre-wrap break-words leading-relaxed`}>
                      {message.type === 'user' ? (
                        message.content
                      ) : (
                        <StreamingChat 
                          content={message.content} 
                          isComplete={message.isComplete} 
                          isUserMessage={false}
                        />
                      )}
                    </div>
                    <div className={`text-xs mt-3 opacity-70 font-medium ${
                      message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Current streaming message */}
            {isStreaming && currentStreamingMessage && (
              <div className="flex justify-start reveal">
                <div className="flex w-full items-end">
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-br from-gray-600 to-gray-800 text-white shadow-lg pulse-glow">
                      <Bot size={18} />
                    </div>
                  </div>
                  <div className="bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200/50 shadow-glow-blue card-modern rounded-2xl px-5 py-4 max-w-4xl">
                    {currentStreamingMessage && (
                      <div className="text-gray-800 leading-relaxed">
                        <StreamingChat 
                          content={currentStreamingMessage} 
                          isComplete={false} 
                          isUserMessage={false}
                        />
                      </div>
                    )}
                    <div className="mt-4 space-y-3">
                      {/* Progress bar for streaming messages */}
                      {currentTaskStatus?.progress !== undefined && currentTaskStatus.progress > 0 && (
                        <ProgressBar 
                          progress={currentTaskStatus.progress} 
                          message={currentTaskStatus.message || t('processing')}
                          size="md"
                        />
                      )}
                      
                      <div className="flex items-center justify-between">
                        {currentTaskStatus && !currentTaskStatus.progress && (
                          <TaskStatus 
                            status={currentTaskStatus.status} 
                            message={currentTaskStatus.message}
                            progress={currentTaskStatus.progress}
                          />
                        )}
                        <div className="flex items-center text-xs text-blue-600 font-semibold ml-auto">
                          <div className="loading-dots mr-2">
                            <div className="dot"></div>
                            <div className="dot"></div>
                            <div className="dot"></div>
                          </div>
                          {t('streaming') || 'AI is responding...'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Loading indicator when starting */}
            {isStreaming && !currentStreamingMessage && (
              <div className="flex justify-start reveal">
                <div className="flex w-full items-end">
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-800 text-white flex items-center justify-center shadow-lg pulse-glow">
                      <Bot size={18} />
                    </div>
                  </div>
                  <div className="bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200/50 shadow-glow card-modern rounded-2xl px-5 py-4 min-w-64 max-w-2xl">
                    <div className="flex items-center mb-3">
                      <div className="loading-dots mr-3">
                        <div className="dot"></div>
                        <div className="dot"></div>
                        <div className="dot"></div>
                      </div>
                      <span className="font-semibold text-gray-800">
                        {currentTaskStatus?.message || t('initializing_task')}
                      </span>
                    </div>
                    {/* Progress bar */}
                    {currentTaskStatus?.progress !== undefined && currentTaskStatus.progress > 0 && (
                      <div className="mt-3">
                        <ProgressBar 
                          progress={currentTaskStatus.progress} 
                          message={t('processing')}
                          size="md"
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <ChatInput
        inputMessage={inputMessage}
        setInputMessage={setInputMessage}
        onSendMessage={handleSendMessage}
        isStreaming={isStreaming}
      />
    </div>
  );
}

export default ChatInterface;