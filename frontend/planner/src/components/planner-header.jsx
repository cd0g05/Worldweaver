// src/components/PlanningHeader.jsx
import React from 'react'
import Icon from './icon.jsx'
import HamburgerMenu from './hamburger-menu.jsx'
import Stepper from './progress-stepper.jsx'

export default function PlanningHeader({ chatIsLoading }) {
    return (
        <header className="w-full bg-[var(--color-background)] shadow-sm px-2 py-1 flex justify-between items-center">
            <Icon />
            <Stepper isDisabled={chatIsLoading} />
            <nav className="flex gap-4 items-center">
                <a href="/dashboard" className="text-[var(--color-text)] hover:text-[var(--color-primary)] font-medium">Dashboard</a>
                <a href="/help" className="text-[var(--color-text)] hover:text-[var(--color-primary)] font-medium">Help</a>
                <a href="/plans" className="text-[var(--color-text)] hover:text-[var(--color-primary)] font-medium">Plans</a>
                <HamburgerMenu />
            </nav>
        </header>
    )
}
