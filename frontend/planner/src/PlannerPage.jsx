import PlannerHeader from "./components/planner-header.jsx";
import DocEditor from "./components/DocEditor.jsx";
import ChatPanel from "./components/LLMChatPanel.jsx";
import React, { useRef } from "react";



function PlannerPage() {
    const editorRef = useRef();

    const handleTestInsert = () => {
        editorRef.current?.insertTextAtStart("Hello, world!\n");
    };
    return (
        <div>
            <PlannerHeader/>
            <div className="grid grid-cols-2 gap-4 p-3 h-[calc(100vh-56px)] bg-[#E3E3E6] overflow-hidden">
                <ChatPanel editorRef={editorRef} />
                <DocEditor ref={editorRef} />

            </div>
        </div>
    );
}
export default PlannerPage;