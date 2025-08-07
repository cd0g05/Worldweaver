// src/components/Icon.jsx
import React from 'react'
// import logo from '../assets/wwprnb.png' // use relative public path, or use import for bundling

export default function Icon() {
    return (
        <a
            href="/frontend/static"
            className="flex items-center space-x-2 opacity-100 transition-opacity hover:opacity-80 text-[#1F2937] hover:text-[#7C3AED] transition-colors duration-200"
        >
            <img src="/static/planning-dist/media/wwprnb.png" alt="Logo" className="h-12 w-auto" />
            <span className="text-xl font-bold">Worldweaver</span>
        </a>
    )
}
