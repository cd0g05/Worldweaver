import React, { useEffect, useImperativeHandle, useState, forwardRef } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Heading from "@tiptap/extension-heading";


const DocEditor = forwardRef((props, ref) => {
    const [animationState, setAnimationState] = useState('idle'); // 'idle', 'glowing', 'fading'

    const editor = useEditor({
        extensions: [StarterKit, Heading.configure({ levels: [1, 2, 3] })],
        content: "",
        onFocus: () => setAnimationState('glowing'),
        onBlur: () => setAnimationState('fading'),
    });

    // Handle animation end to clean up state
    useEffect(() => {
        if (animationState === 'fading') {
            const timer = setTimeout(() => {
                setAnimationState('idle');
            }, 800); // Match the fade-out duration
            return () => clearTimeout(timer);
        }
    }, [animationState]);

    // Expose editor methods to parent via ref
    useImperativeHandle(ref, () => ({
        getJSON: () => editor?.getJSON(),
        setText: (text) => editor?.commands.setContent(text),
        insertTextAtStart: (text) => editor?.commands.insertContentAt(0, text),
        clearAll: () => editor?.commands.clearContent(),
        startGlow: () => setAnimationState('glowing'),
        stopGlow: () => setAnimationState('fading'),
        triggerGlow: (duration = 2000) => {
            setAnimationState('glowing');
            setTimeout(() => setAnimationState('fading'), duration);
        },
        editor,
    }));

    const focusEditor = () => {
        if (editor && !editor.isFocused) {
            editor.commands.focus();
        }
    };

    const getAnimationClass = () => {
        switch (animationState) {
            case 'glowing':
                return 'animate-glow-pulse border-transparent';
            case 'fading':
                return 'animate-glow-fade-out border-transparent';
            default:
                return '';
        }
    };

    return (
        <div
            onClick={focusEditor}
            className={`transition-all duration-300 h-[calc(100vh-85px)] overflow-auto rounded-2xl shadow-lg px-4 pt-2 bg-white cursor-text ${getAnimationClass()}`}
        >
            {editor ? (
                <EditorContent editor={editor} className="prose max-w-none focus:outline-none m-2" />
            ) : (
                <p>Loading editor...</p>
            )}
        </div>
    );
});

export default DocEditor;