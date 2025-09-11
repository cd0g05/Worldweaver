import React, { useState } from 'react';
import aiIcon from '../../assets/react.svg';
import ReactMarkdown from 'react-markdown'

// Polyfill for crypto.randomUUID() for older browsers
const generateUUID = () => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    // Fallback for older browsers
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

// Message type constants
const MESSAGE_TYPES = {
    USER: 'user',
    ASSISTANT: 'assistant',
    TOOL: 'tool',
    ERROR: 'error'
};

const MessageItem = ({ message }) => {
    const [showDetails, setShowDetails] = useState(false);

    // Get styling based on message type
    const getMessageStyle = () => {
        switch (message.type) {
            case MESSAGE_TYPES.USER:
                return {
                    container: 'bg-blue-50 border-blue-200 ml-auto max-w-[80%]',
                    header: 'text-blue-800',
                    icon: '👤'
                };
            case MESSAGE_TYPES.ASSISTANT:
                return {
                    container: 'bg-gray-50 border-gray-200 mr-auto max-w-[80%]',
                    header: 'text-gray-800',
                    icon: '🤖'
                };
            case MESSAGE_TYPES.TOOL:
                return {
                    container: 'bg-purple-50 border-purple-200 mx-auto max-w-[90%]',
                    header: 'text-purple-800',
                    icon: '🔧'
                };
            case MESSAGE_TYPES.ERROR:
                return {
                    container: 'bg-red-50 border-red-200 mx-auto max-w-[90%]',
                    header: 'text-red-800',
                    icon: '⚠️'
                };
            default:
                return {
                    container: 'bg-gray-50 border-gray-200 mx-auto max-w-[90%]',
                    header: 'text-gray-800',
                    icon: '💬'
                };
        }
    };

    // Format timestamp for display
    const formatTime = (timestamp) => {
        if (!timestamp) return '';

        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;

        return date.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Get display name for message type
    const getDisplayName = () => {
        switch (message.type) {
            case MESSAGE_TYPES.USER:
                return 'You';
            case MESSAGE_TYPES.ASSISTANT:
                return 'AI Assistant';
            case MESSAGE_TYPES.TOOL:
                return `Tool: ${message.tool || 'Unknown'}`;
            case MESSAGE_TYPES.ERROR:
                return 'Error';
            default:
                return 'Message';
        }
    };

    // Render tool parameters in a readable way
    const renderToolParams = () => {
        if (!message.params) return null;

        const filteredParams = { ...message.params };
        // Remove common fields that aren't interesting to display
        delete filteredParams.type;
        delete filteredParams.description;
        delete filteredParams.timestamp;

        return (
            <div className="mt-3 p-3 bg-white bg-opacity-50 rounded-lg">
                <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="text-xs text-purple-600 hover:text-purple-800 font-medium mb-2 flex items-center space-x-1"
                >
                    <span>{showDetails ? '▼' : '▶'}</span>
                    <span>Parameters</span>
                </button>

                {showDetails && (
                    <div className="space-y-1">
                        {Object.entries(filteredParams).map(([key, value]) => (
                            <div key={key} className="flex text-xs">
                <span className="font-medium text-gray-600 w-20 capitalize">
                  {key}:
                </span>
                                <span className="text-gray-800 flex-1 break-words">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    // Render the main message content
    const renderContent = () => {
        switch (message.type) {
            case MESSAGE_TYPES.TOOL:
                return (
                    <div>
                        <p className="text-sm text-gray-700 mb-2">
                            {message.description || `Executed ${message.tool} command`}
                        </p>
                        {message.tool && (
                            <div className="inline-block bg-white bg-opacity-70 px-2 py-1 rounded text-xs font-mono text-purple-700">
                                <ReactMarkdown>{message.tool}</ReactMarkdown>
                            </div>
                        )}
                        {renderToolParams()}
                    </div>
                );

            case MESSAGE_TYPES.ERROR:
                return (
                    <div>
                        <p className="text-sm text-red-700 font-medium">
                            <ReactMarkdown>{message.content || message.error || 'An error occurred'}</ReactMarkdown>
                        </p>
                        {message.details && (
                            <p className="text-xs text-red-600 mt-1 opacity-80">
                                {message.details}
                            </p>
                        )}
                    </div>
                );

            default:
                return (
                    <p className="text-sm whitespace-pre-wrap text-gray-800 leading-relaxed">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                    </p>
                );
        }
    };

    const style = getMessageStyle();

    return (
        <div className={`border rounded-xl p-4 mb-3 shadow-sm transition-all duration-200 hover:shadow-md ${style.container}`}>
            {/* Message Header */}
            <div className="flex justify-between items-center mb-2">
                <div className="flex items-center space-x-2">
                    <span className="text-lg">{style.icon}</span>
                    <span className={`text-sm font-semibold ${style.header}`}>
            {getDisplayName()}
          </span>
                </div>
                <span className="text-xs text-gray-500">
          {formatTime(message.timestamp)}
        </span>
            </div>

            {/* Message Content */}
            <div className="mt-2">
                {renderContent()}
            </div>

            {/* Debug info for development */}
            {process.env.NODE_ENV === 'development' && (
                <details className="mt-3">
                    <summary className="text-xs text-gray-400 cursor-pointer">
                        Debug Info
                    </summary>
                    <pre className="text-xs bg-gray-100 p-2 mt-1 rounded overflow-x-auto">
            {JSON.stringify(message, null, 2)}
          </pre>
                </details>
            )}
        </div>
    );
};

// Helper functions to create different message types
export const createUserMessage = (content) => ({
    id: generateUUID(),
    type: MESSAGE_TYPES.USER,
    content,
    timestamp: Date.now()
});

export const createAssistantMessage = (content) => ({
    id: generateUUID(),
    type: MESSAGE_TYPES.ASSISTANT,
    content,
    timestamp: Date.now()
});

export const createToolMessage = (toolData) => ({
    id: generateUUID(),
    type: MESSAGE_TYPES.TOOL,
    tool: toolData.tool,
    description: toolData.description,
    params: toolData,
    timestamp: Date.now()
});

export const createErrorMessage = (error, details = null) => ({
    id: generateUUID(),
    type: MESSAGE_TYPES.ERROR,
    content: error,
    details,
    timestamp: Date.now()
});

// Export message types for use in other components
export { MESSAGE_TYPES };
export default MessageItem;