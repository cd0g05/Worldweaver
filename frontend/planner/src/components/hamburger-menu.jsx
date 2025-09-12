// src/components/HamburgerMenu.jsx
import React, { useState, useRef, useEffect } from 'react'

export default function HamburgerMenu() {
    const [open, setOpen] = useState(false)
    const dropdownRef = useRef(null)

    // Close menu when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [])

    return (
        <div className="relative inline-block text-left z-50" ref={dropdownRef}>
            <button
                onClick={() => setOpen(!open)}
                className="p-2 rounded-md hover:bg-[var(--color-primary)]/20 focus:outline-none"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6 text-[var(--color-text)]"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>

            {open && (
                <div className="absolute right-0 mt-2 w-40 origin-top-right rounded-md bg-[var(--color-background)] shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transition ease-out duration-100">
                    <div className="py-1">
                        {/* You can optionally add user info here */}
                        <a href="/account" className="block px-4 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-primary)] hover:text-white">Account</a>
                        <a href="/help" className="block px-4 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-primary)] hover:text-white">Help</a>
                        <a href="/logout" className="block w-full text-left px-4 py-2 text-sm text-[var(--color-text)] hover:bg-[var(--color-primary)] hover:text-white">Logout</a>
                    </div>
                </div>
            )}
        </div>
    )
}
