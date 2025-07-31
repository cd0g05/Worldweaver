import PlannerHeader from "./components/planner-header.jsx";
import DocEditor from "./components/DocEditor.jsx";
import LLMPanel from "./components/LLMChatPanel.jsx";
import React, { useRef } from "react";



function PlannerPage() {
    const editorRef = useRef();

    const handleTestInsert = () => {
        editorRef.current?.insertTextAtStart("Hello, world!\n");
    };
    return (
        <div>
            <PlannerHeader/>
            <div className="grid grid-cols-2 gap-4 p-6 h-[calc(100vh-80px)] bg-[#E3E3E6]">
                <LLMPanel/>
                <DocEditor ref={editorRef} />
            </div>
        </div>
    );
}
export default PlannerPage;