import PlannerHeader from "./components/planner-header.jsx";
import DocEditor from "./components/DocEditor.jsx";
import ChatPanel from "./components/LLMChatPanel.jsx";
import React, { useRef, useState } from "react";
import { useStage } from "./StageContext.jsx"; // Import the hook

function PlannerPage() {
    const editorRef = useRef();
    const [chatIsLoading, setChatIsLoading] = useState(false);

    // ✅ Get stage from context instead of local state
    const { linearStage } = useStage();

    const handleTestInsert = () => {
        editorRef.current?.insertTextAtStart("Hello, world!\n");
    };

    return (
        <div>
            {/* ✅ No more prop drilling needed */}
            <PlannerHeader chatIsLoading={chatIsLoading} />
            <div className="grid grid-cols-2 gap-4 p-3 h-[calc(100vh-56px)] bg-[#E3E3E6] overflow-hidden">
                <ChatPanel
                    editorRef={editorRef}
                    onLoadingChange={setChatIsLoading}
                    // currentStage={linearStage} // ✅ Use linearStage from context
                />
                <DocEditor ref={editorRef} />
            </div>
        </div>
    );
}
export default PlannerPage;