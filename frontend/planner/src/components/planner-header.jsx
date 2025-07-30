// src/components/PlanningHeader.jsx
import React from 'react'
import Icon from './icon.jsx' // You'll create this from icon.html
import HamburgerMenu from './hamburger-menu.jsx' // You'll create this from hamburger_menu_r.html

export default function PlanningHeader() {
    return (
        <header className="w-full bg-white shadow-sm px-6 py-4 flex justify-between items-center">
            <Icon />

            <nav className="flex gap-4 items-center">
                <a href="/dashboard" className="text-gray-700 hover:text-indigo-600 font-medium">Dashboard</a>
                <a href="/help" className="text-gray-700 hover:text-indigo-600 font-medium">Help</a>
                <a href="/plans" className="text-gray-700 hover:text-indigo-600 font-medium">Plans</a>

                <HamburgerMenu />
            </nav>
        </header>
    )
}
