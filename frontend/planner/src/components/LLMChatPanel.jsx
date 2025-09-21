import React, { useState, useRef, useCallback, useEffect } from 'react';
import MessageList from './llm_components/MessageList.jsx';
import ChatInput from './llm_components/ChatInput.jsx';
import { createUserMessage, createAssistantMessage, createToolMessage, createErrorMessage } from './llm_components/MessageItem';
import { useStage, useStageEvents, STAGE_EVENTS } from '../StageContext.jsx';

const ChatPanel = ({ editorRef, onLoadingChange }) => {
    // This is the shared state that both components will use
    const [messages, setMessages] = useState([createAssistantMessage("**Welcome to Worldweaver!**\n" +
    "This app is designed to help you plan and develop your fantasy story through a guided, step-by-step process. Whether you're a first-time writer or an experienced author, Worldweaver will walk you through everything from your initial big idea all the way to detailed plot planning.\n" +
    "Here's how it works: You'll move through different stages, each focusing on a specific aspect of your story (like your main concept, worldbuilding, characters, and plot). In each stage, you'll have a conversation with an AI assistant that will help you brainstorm, refine your ideas, and organize your thoughts. At the end of each stage, your progress will be automatically added to your planning document.\n" +
    "The best part? This is completely flexible. You can edit anything in your planning document at any time, ask for help refining your ideas, or even skip stages that don't feel relevant to your story.\n" +
    "\n**Your first task:** \nSend a message to the AI assistant! It can be anything, a question, a comment, or simply say hello!")]);
    const [isLoading, setIsLoading] = useState(false);
    const { linearStage } = useStage();
    const stageHistoryRef = useRef({});
    const globalHistoryRef = useRef(null);
    // Function to add a message to the list
    const addMessage = (message) => {
        setMessages(prev => [...prev, message]);
    };

    useEffect(() => {
        if (onLoadingChange) {
            onLoadingChange(isLoading);
        }
    }, [isLoading, onLoadingChange]);

    const pruneHistory = async (messagesToPrune) => {
        setIsLoading(true);
        try {
            const response = await fetch('/prune', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    history: messagesToPrune
                })
            });
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            else {
                const prunedData = await response.json();
                globalHistoryRef.current = prunedData.text;
                console.log("Saved Chat Context", globalHistoryRef.current);
            }
        } catch (error) {
            console.error('Error with pruning process:', error);

            // Add error message to chat
            const errorMessage = createErrorMessage(
                'Issue migrating chat history',
                error.message
            );
            addMessage(errorMessage);
        } finally {
            // 6. Clear loading state
            setIsLoading(false);
        }
    }
    const getTutorial = async (newStage) => {
        setIsLoading(true);
        try {
            const response = await fetch('/tutorial', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    stage: newStage.linear,
                    chat_context: " ",
                    doc_context: " "
                })
            });
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            else {
                // response should be { type: "message", text:"tutorial text..."}
                const tutorialMessage = await response.json();
                return tutorialMessage.text;
            }
        } catch (error) {
            console.error('Error with tutorial process:', error);
            const errorMessage = createErrorMessage(
                'Issue delivering tutorial',
                error.message
            );
            addMessage(errorMessage);
        } finally {
            // 6. Clear loading state
            setIsLoading(false);
        }
    }

    useStageEvents(STAGE_EVENTS.STAGE_CHANGED, async (event) => {
        const { oldStage, newStage } = event.detail;
        console.log("Stage change triggered:", newStage);

        // Use the functional form of setMessages to get current state
        setMessages(currentMessages => {

            // Get previously saved messages for this stage
            const previouslySavedMessages = stageHistoryRef.current[oldStage.linear] || [];

            // Compare current messages with previously saved messages
            const previousMessageCount = previouslySavedMessages.length;
            const currentMessageCount = currentMessages.length;
            const newMessageCount = currentMessageCount - previousMessageCount;
            // console.log(`📊 Stage ${oldStage.linear}: Previously saved: ${previousMessageCount}, Current: ${currentMessageCount}, New: ${newMessageCount}`);

            // Save current messages to history
            stageHistoryRef.current[oldStage.linear] = [...currentMessages];

            // Prune if needed (don't await here to avoid blocking)
            // if (newMessageCount > 1) {
            //     const newMessages = currentMessages.slice(previousMessageCount);
            //     // console.log(`🔄 Pruning ${newMessages.length} new messages for stage ${oldStage.linear}`);
            //     // console.log('New messages to prune:', newMessages.map(msg => `${msg.type}: ${msg.content?.substring(0, 50)}...`));
            //     pruneHistory(newMessages);
            // }

            // Restore or create new messages
            const savedHistory = stageHistoryRef.current[newStage.linear];
            if (savedHistory) {
                return savedHistory;
            } else {

            // ----------------------------------------
            // TODO: Make this set the tutorial message
            // ----------------------------------------
                return [];
            }
        });
        const savedHistory = stageHistoryRef.current[newStage.linear];
        if (!savedHistory) {
            try {
                const tutorial = await getTutorial(newStage); // ✅ Await the Promise
                const tutorialMessage = createAssistantMessage(tutorial);
                setMessages(prev => [tutorialMessage]); // ✅ Add tutorial message
            } catch (error) {
                console.error('Failed to get tutorial:', error);
                // Fallback to hardcoded message
                const fallbackMessage = createAssistantMessage("Welcome to this new stage, ask the AI Assistant what to do!");
                setMessages(prev => [fallbackMessage]);
            }
        }
    });


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
            // console.log("Current Stage: ", linearStage);
            const response = await fetch('/llm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: userInput,
                    document: docContext,
                    chat_history: messages,
                    stage: linearStage
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

            } else if (data.type === 'document') {
                const toolMessage = createToolMessage(data.document);
                addMessage(toolMessage);
                executeToolCall(data.document);
                editorRef?.current?.triggerGlow(1500);
            } else if (data.type === 'both') {
                const assistantMessage = createAssistantMessage(data.text);
                addMessage(assistantMessage);
                const toolMessage = createToolMessage(data.document);
                addMessage(toolMessage);
                executeToolCall(data.document);
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
                    // if (toolData.index) {
                    //     editor.commands.insertContentAt(toolData.index || 0, toolData.text);
                    // }
                    // else {
                        editor.commands.insertContent(toolData.text);
                    // }

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