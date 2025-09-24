import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';

const TaskStatus = ({ status, message, progress = 0 }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'failed':
      case 'error':
        return <AlertCircle className="text-red-500" size={16} />;
      case 'running':
      case 'processing':
        return <Loader2 className="text-blue-500 animate-spin" size={16} />;
      default:
        return <Clock className="text-yellow-500" size={16} />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'failed':
      case 'error':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'running':
      case 'processing':
        return 'text-blue-700 bg-blue-50 border-blue-200';
      default:
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border text-sm ${getStatusColor()}`}>
      {getStatusIcon()}
      <span>{message || status}</span>
      {progress > 0 && progress < 100 && (
        <span className="text-xs">({progress}%)</span>
      )}
    </div>
  );
};

export default TaskStatus;