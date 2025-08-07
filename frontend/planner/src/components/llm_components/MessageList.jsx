import React, { useRef, useEffect } from 'react';
import MessageItem from './MessageItem';

const MessageList = ({ messages = [] }) => {
    const messagesEndRef = useRef(null);

    // Simple auto-scroll: always scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Render the container with fixed height and internal scrolling
    return (
        <div className="flex-1 overflow-y-auto p-4 min-h-0" >
            {/* Empty state when no messages */}
            {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full min-h-[430px]">
                    <div className="text-center text-gray-500">
                        <div className="text-4xl mb-4">💬</div>
                        <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
                        <p className="text-sm">Send a message to begin chatting with the AI assistant</p>
                    </div>
                </div>
            ) : (
                /* Messages list with proper spacing */
                <div className="space-y-3 min-h-[430px]">
                    {messages.map((message) => (
                        <MessageItem key={message.id} message={message} />
                    ))}

                    {/* Invisible element at the bottom for auto-scroll */}
                    <div ref={messagesEndRef} />
                </div>
            )}
        </div>
    );
};

export default MessageList;