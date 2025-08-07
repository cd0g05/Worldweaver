import React, { useState } from 'react';
import MessageList from './llm_components/MessageList.jsx';
import ChatInput from './llm_components/ChatInput.jsx';
import { createUserMessage, createAssistantMessage, createToolMessage, createErrorMessage } from './llm_components/MessageItem';

const ChatPanel = ({ editorRef }) => {
    // This is the shared state that both components will use
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Function to add a message to the list
    const addMessage = (message) => {
        setMessages(prev => [...prev, message]);
    };

    // Function that ChatInput will call when user sends a message
    const handleSendMessage = async (userInput) => {
        // 1. Add user message to the chat
        const userMessage = createUserMessage(userInput);
        addMessage(userMessage);

        // 2. Set loading state
        setIsLoading(true);

        try {
            // 3. Get document context from editor (if available)
            const docContext = editorRef?.current?.getJSON();

            // 4. Send to your /llm endpoint
            const response = await fetch('/llm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: userInput,
                    document: docContext,
                    chat_history: messages
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            // 5. Handle different response types
            if (data.type === 'tool') {
                // Create tool message and add to chat
                const toolMessage = createToolMessage(data);
                addMessage(toolMessage);

                // Execute the tool on the editor
                executeToolCall(data);

                // Trigger editor glow effect
                editorRef?.current?.triggerGlow(1500);

            } else if (data.type === 'message') {
                // Create assistant message and add to chat
                const assistantMessage = createAssistantMessage(data.text);
                addMessage(assistantMessage);

            } else {
                // Unknown response type
                const errorMessage = createErrorMessage(
                    'Unknown response format',
                    `Received type: ${data.type}`
                );
                addMessage(errorMessage);
            }

        } catch (error) {
            console.error('Error sending message:', error);

            // Add error message to chat
            const errorMessage = createErrorMessage(
                'Failed to send message',
                error.message
            );
            addMessage(errorMessage);

        } finally {
            // 6. Clear loading state
            setIsLoading(false);
        }
    };

    // Execute tool calls on the editor
    const executeToolCall = (toolData) => {
        try {
            const editor = editorRef?.current?.editor;
            if (!editor) {
                console.error('Editor not available');
                return;
            }

            switch (toolData.tool) {
                case 'set':
                    editorRef.current.setText(toolData.text);
                    break;
                case 'insert':
                    editor.commands.insertContentAt(toolData.index || 0, toolData.text);
                    break;
                case 'delete':
                    if (toolData.index !== undefined && toolData.length !== undefined) {
                        editor.commands.deleteRange({
                            from: toolData.index,
                            to: toolData.index + toolData.length
                        });
                    }
                    break;
                case 'deleteall':
                    editorRef.current.clearAll();
                    break;
                case 'format':
                    // Handle text formatting
                    if (toolData.index !== undefined && toolData.length !== undefined) {
                        editor.commands.setTextSelection({
                            from: toolData.index,
                            to: toolData.index + toolData.length
                        });
                        // Apply formatting based on toolData.formats
                    }
                    break;
                case 'update':
                    if (toolData.index !== undefined && toolData.length !== undefined) {
                        editor.commands.deleteRange({
                            from: toolData.index,
                            to: toolData.index + toolData.length
                        });
                        editor.commands.insertContentAt(toolData.index, toolData.text);
                        break;
                    }
                default:
                    console.warn('Unknown tool:', toolData.tool);
            }
        } catch (error) {
            console.error('Error executing tool:', error);

            // Add error message to chat
            const errorMessage = createErrorMessage(
                'Tool execution failed',
                `Failed to execute ${toolData.tool}: ${error.message}`
            );
            addMessage(errorMessage);
        }
    };

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Header */}
            {/*<div className="flex-shrink-0 p-2 pl-4 rounded-t-2xl">*/}
            {/*    <h2 className="text-m font-semibold">AI Assistant</h2>*/}
            {/*    <p className="text-xs text-gray-600">*/}
            {/*        {messages.length === 0 ? 'Ready to chat' : `${messages.length} messages`}*/}
            {/*    </p>*/}
            {/*</div>*/}

            {/* Messages Area - MessageList receives the messages array */}
            <MessageList messages={messages} />

            {/* Loading Indicator */}
            {isLoading && (
                <div className="flex-shrink-0 px-4 py-2 border-t border-gray-100">
                    <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                        <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                            <span className="text-sm text-gray-600">AI is thinking...</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Input Area - ChatInput receives the send function */}
            <ChatInput
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
            />
        </div>
    );
};

export default ChatPanel;