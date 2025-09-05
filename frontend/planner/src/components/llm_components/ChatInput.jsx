import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

const ChatInput = ({ onSendMessage, isLoading = false }) => {
    const [inputValue, setInputValue] = useState('');
    const textareaRef = useRef(null);

    // Auto-resize textarea function
    const autoResize = (textarea) => {
        if (!textarea) return;

        // Reset height to auto to get the correct scrollHeight
        textarea.style.height = 'auto';

        // Set height to scrollHeight (content height)
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    };

    // Handle textarea changes
    const handleInputChange = (e) => {
        setInputValue(e.target.value);
        autoResize(e.target);
    };

    // Handle key presses
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Send message function
    const handleSend = async () => {
        if (!inputValue.trim() || isLoading) return;

        // Call the function passed down from ChatContainer
        if (onSendMessage) {
            onSendMessage(inputValue);
        }

        // Clear input
        setInputValue('');

        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    // Auto-resize on component mount
    useEffect(() => {
        autoResize(textareaRef.current);
    }, []);
    // border-t border-gray-200 bg-white
    return (
        <div className="p-4  rounded-b-2xl">
            <div className="flex space-x-3 items-end">
                <div className="flex-1 relative">

                    <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="w-full border bg-white border-gray-300 rounded-4xl px-4 py-3 pr-16 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent min-h-[50px] max-h-[200px] overflow-y-auto transition-all duration-200"
              disabled={isLoading}
              rows="1"
          />

                    {/* Send button positioned inside textarea */}
                    <button
                        onClick={handleSend}
                        disabled={isLoading || !inputValue.trim()}
                        className="absolute right-2 bottom-3 bg-purple-600 text-white px-4 py-2 rounded-full hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm font-medium"
                    >
                        {isLoading ? (
                            <div className="flex items-center space-x-2">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                <span>Sending...</span>
                            </div>
                        ) : (
                            'Send'
                        )}
                    </button>
                </div>
            </div>

            {/*/!* Debug info - remove this later *!/*/}
            {/*<div className="mt-2 text-xs text-gray-500">*/}
            {/*    Character count: {inputValue.length} |*/}
            {/*    Status: {isLoading ? 'Sending...' : 'Ready'} |*/}
            {/*    Check console for server responses*/}
            {/*</div>*/}
        </div>
    );
};

export default ChatInput;