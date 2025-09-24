import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import StreamingChat from './components/StreamingChat.jsx';
import TaskStatus from './components/TaskStatus.jsx';
import ExampleQueries from './components/ExampleQueries.jsx';
import ProgressBar from './components/ProgressBar.jsx';

function App() {
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
    setCurrentTaskStatus({ status: 'starting', message: 'Initializing task...' });

    try {
      const response = await fetch('http://localhost:8000/api/v1/agent/tasks/execute-stream', {
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
          errorMessage = 'Validation error: The request data is invalid or incomplete';
        } else if (response.status === 500) {
          errorMessage = 'Server error: An internal server error occurred';
        } else if (response.status === 404) {
          errorMessage = 'Not found: The requested endpoint was not found';
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
                setCurrentTaskStatus({ status: 'running', message: 'Task started' });
              } else if (data.type === 'task_status') {
                const statusData = data.data || {};
                setCurrentTaskStatus({ 
                  status: statusData.status || 'running', 
                  message: statusData.message || 'Processing...', 
                  progress: statusData.progress
                });
              } else if (data.type === 'planning_update') {
                const planningData = data.data || {};
                if (planningData.type === 'status') {
                  const statusData = planningData.data || {};
                  setCurrentTaskStatus({ 
                    status: 'planning', 
                    message: statusData.message || 'Planning...', 
                    progress: statusData.progress || 0
                  });
                } else {
                  // Handle direct planning_update data structure
                  setCurrentTaskStatus({ 
                    status: 'planning', 
                    message: planningData.message || 'Planning...', 
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
                      message: toolData.message || 'Processing...', 
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
                  setCurrentTaskStatus({ status: 'completed', message: 'Execution completed' });
                }
              } else if (data.type === 'task_completed') {
                const result = data.data?.result || '';
                if (result) {
                  fullResponse = result;
                  setCurrentStreamingMessage(result);
                }
                setCurrentTaskStatus({ status: 'completed', message: 'Task completed successfully' });
              } else if (data.type === 'task_failed') {
                setCurrentTaskStatus({ status: 'failed', message: 'Task failed' });
              } else if (data.type === 'error') {
                // Handle backend errors (like JSON serialization errors)
                const errorData = data.data || {};
                const errorMessage = errorData.error || 'An unknown error occurred';
                console.error('Backend error:', errorMessage);
                
                // Set error status and break the streaming loop
                setCurrentTaskStatus({ status: 'failed', message: `Error: ${errorMessage}` });
                throw new Error(errorMessage);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
              // If it's our custom error, re-throw it to be handled by the outer catch
              if (e.message !== 'Unexpected end of JSON input') {
                throw e;
              }
            }
          }
        }
      }

      // Add the final bot message
      if (fullResponse || currentStreamingMessage) {
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
        displayError = 'The server encountered a data formatting issue. This may be due to datetime serialization problems in the backend.';
      } else if (error.message.includes('422')) {
        displayError = 'There was a validation error with your request. Please try rephrasing your question.';
      } else if (error.message.includes('Failed to fetch')) {
        displayError = 'Unable to connect to the server. Please check if the backend service is running on port 8000.';
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `❌ **Error**: ${displayError}\n\n*Technical details: ${error.message}*`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsStreaming(false);
      setCurrentStreamingMessage('');
      setCurrentTaskStatus(null);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <Bot className="mr-3 text-blue-600" size={32} />
            ReWOO Streaming Chat
          </h1>
          <p className="text-gray-600 mt-1">
            AI-powered research and task execution with real-time streaming
          </p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-4xl mx-auto h-full">
          <div className="h-full overflow-y-auto custom-scrollbar p-4 space-y-4">
            {messages.length === 0 && !isStreaming && (
              <div className="text-center text-gray-500 mt-8">
                <Bot size={48} className="mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Welcome to ReWOO Chat!</p>
                <p className="text-sm mt-2 mb-8">Ask me anything and I'll help you with research and tasks.</p>
                <div className="max-w-4xl mx-auto">
                  <ExampleQueries onSelectQuery={setInputMessage} />
                </div>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex w-full ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-end`}>
                  <div className={`flex-shrink-0 ${message.type === 'user' ? 'ml-3' : 'mr-3'}`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-md ${
                      message.type === 'user' 
                        ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white' 
                        : message.isError 
                        ? 'bg-red-500 text-white'
                        : 'bg-gradient-to-r from-gray-600 to-gray-700 text-white'
                    }`}>
                      {message.type === 'user' ? <User size={20} /> : <Bot size={20} />}
                    </div>
                  </div>
                  <div
                    className={`rounded-xl px-4 py-3 ${
                      message.type === 'user' 
                        ? 'max-w-2xl bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg' 
                        : message.isError
                        ? 'max-w-4xl bg-red-50 text-red-800 border border-red-200 shadow-sm'
                        : 'max-w-4xl bg-white text-gray-800 border border-gray-200 shadow-sm'
                    }`}
                  >
                    <div className={`${message.type === 'user' ? 'text-white' : 'text-gray-800'} whitespace-pre-wrap break-words`}>
                      {message.type === 'user' ? (
                        <div className="text-white">{message.content}</div>
                      ) : (
                        <StreamingChat 
                          content={message.content} 
                          isComplete={message.isComplete} 
                          isUserMessage={false}
                        />
                      )}
                    </div>
                    <div className={`text-xs mt-2 opacity-75 ${
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
              <div className="flex justify-start">
                <div className="flex w-full items-end">
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 text-white flex items-center justify-center shadow-md">
                      <Bot size={20} />
                    </div>
                  </div>
                  <div className="bg-white text-gray-800 border border-gray-200 shadow-sm rounded-xl px-4 py-3 max-w-4xl">
                    {currentStreamingMessage && (
                      <div className="text-gray-800">
                        <StreamingChat 
                          content={currentStreamingMessage} 
                          isComplete={false} 
                          isUserMessage={false}
                        />
                      </div>
                    )}
                    <div className="mt-3 space-y-2">
                      {/* Progress bar for streaming messages */}
                      {currentTaskStatus?.progress !== undefined && currentTaskStatus.progress > 0 && (
                        <ProgressBar 
                          progress={currentTaskStatus.progress} 
                          message={currentTaskStatus.message || 'Processing...'}
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
                        <div className="flex items-center text-xs text-blue-600 font-medium ml-auto">
                          <Loader2 className="animate-spin mr-2" size={12} />
                          Streaming...
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Loading indicator when starting */}
            {isStreaming && !currentStreamingMessage && (
              <div className="flex justify-start">
                <div className="flex w-full items-end">
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 text-white flex items-center justify-center shadow-md">
                      <Bot size={20} />
                    </div>
                  </div>
                  <div className="bg-white text-gray-800 border border-gray-200 shadow-sm rounded-xl px-4 py-3 min-w-64 max-w-2xl">
                    <div className="flex items-center mb-2">
                      <Loader2 className="animate-spin mr-2 text-blue-600" size={16} />
                      <span className="font-medium text-gray-800">
                        {currentTaskStatus?.message || 'Thinking...'}
                      </span>
                    </div>
                    {/* Progress bar */}
                    {currentTaskStatus?.progress !== undefined && currentTaskStatus.progress > 0 && (
                      <div className="mt-2">
                        <ProgressBar 
                          progress={currentTaskStatus.progress} 
                          message="Progress"
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
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                className="w-full resize-none border-2 border-gray-200 rounded-xl px-4 py-3 text-gray-800 placeholder-gray-400 bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none font-medium shadow-sm transition-all duration-200 hover:border-gray-300"
                rows="2"
                disabled={isStreaming}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isStreaming}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed text-white font-semibold rounded-xl px-6 py-3 flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none disabled:hover:scale-100"
            >
              {isStreaming ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <Send size={20} />
              )}
              <span>{isStreaming ? 'Sending...' : 'Send'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;