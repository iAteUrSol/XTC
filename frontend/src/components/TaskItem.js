import React from 'react';

/**
 * TaskItem component - Renders an individual task with completion toggle and actions
 * 
 * @param {Object} props - Component props
 * @param {Object} props.task - Task object with id, title, description, completed status
 * @param {Function} props.onToggleComplete - Function to toggle task completion status
 * @returns {JSX.Element} - Rendered component
 */
function TaskItem({ task, onToggleComplete }) {
  // Define due date formatting if task has a dueDate
  const formattedDueDate = task.dueDate 
    ? new Date(task.dueDate).toLocaleDateString() 
    : null;
  
  // Determine priorityCss based on task priority
  let priorityIndicator = null;
  if (task.priority) {
    let priorityColor = '';
    let priorityLabel = '';
    
    switch(task.priority.toLowerCase()) {
      case 'high':
        priorityColor = 'bg-red-500';
        priorityLabel = 'High';
        break;
      case 'medium':
        priorityColor = 'bg-yellow-500';
        priorityLabel = 'Medium';
        break;
      case 'low':
        priorityColor = 'bg-green-500';
        priorityLabel = 'Low';
        break;
      default:
        priorityColor = 'bg-gray-500';
        priorityLabel = task.priority;
    }
    
    priorityIndicator = (
      <span className={`${priorityColor} text-white text-xs px-2 py-1 rounded-full`}>
        {priorityLabel}
      </span>
    );
  }
  
  return (
    <li className="py-3">
      <div className="flex items-start">
        {/* Checkbox for completion status */}
        <div className="flex-shrink-0 mt-1">
          <input 
            type="checkbox" 
            checked={task.completed} 
            onChange={onToggleComplete}
            className="h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          />
        </div>
        
        {/* Task content */}
        <div className="ml-3 flex-1">
          <div className="flex items-center justify-between">
            <h3 className={`text-lg font-medium ${task.completed ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
              {task.title}
            </h3>
            
            {/* Task actions */}
            <div className="flex space-x-2">
              {priorityIndicator}
              
              <button 
                className="text-gray-500 hover:text-gray-700"
                aria-label="Edit task"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
              </button>
              
              <button 
                className="text-gray-500 hover:text-red-600"
                aria-label="Delete task"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* Task description */}
          {task.description && (
            <p className={`mt-1 text-sm ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
              {task.description}
            </p>
          )}
          
          {/* Task metadata */}
          <div className="mt-2 flex items-center text-xs text-gray-500">
            {/* Due date if available */}
            {formattedDueDate && (
              <div className="flex items-center mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{formattedDueDate}</span>
              </div>
            )}
            
            {/* Category if available */}
            {task.category && (
              <div className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                <span>{task.category}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </li>
  );
}

export default TaskItem;
