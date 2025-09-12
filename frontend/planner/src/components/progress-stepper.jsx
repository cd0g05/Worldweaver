import React, { useEffect } from 'react'
import { useStage } from '../StageContext.jsx'

export default function ProgressStepper({ isDisabled = false}) {
    const {
        currentMajorStage,
        currentSubStage,
        totalSubStages,
        stageConfig,
        currentStageProgress,
        canGoNext,
        canGoPrevious,
        advanceStage,
        goToPreviousStage,
        currentSubStageName
    } = useStage();

    const effectiveCanGoNext = canGoNext && !isDisabled;
    const effectiveCanGoPrevious = canGoPrevious && !isDisabled;

    // Calculate which stages to show (current + next 2)
    const getVisibleStages = () => {
        const startIndex = currentMajorStage - 1; // Convert to 0-based index
        const endIndex = Math.min(startIndex + 3, stageConfig.length); // Show 3 stages max

        return stageConfig.slice(startIndex, endIndex);
    };

    const visibleStages = getVisibleStages();

    const handleAdvance = () => {
        if (!isDisabled) {
            advanceStage();
        }
    };

    const handlePrevious = () => {
        if (!isDisabled) {
            goToPreviousStage();
        }
    };

    return (
        <div className="w-1/2 mx-auto bg-[var(--color-background)] px-2 py-1">
            {/* Major Stages Progress Bar - Sliding Window */}
            <div className="flex items-center justify-center mb-1">
                {/* Show dots for previous stages if not visible */}
                {currentMajorStage > 1 && (
                    <>
                        <div className="flex items-center">
                            <div className="w-1 h-1 rounded-full bg-[var(--color-success)] mx-0.5"></div>
                            <div className="w-0.5 h-0.5 rounded-full bg-[var(--color-border)] mx-0.5"></div>
                            <div className="w-0.5 h-0.5 rounded-full bg-[var(--color-border)] mx-0.5"></div>
                        </div>
                        <div className="h-0.5 w-2 bg-[var(--color-success)] mx-1"></div>
                    </>
                )}

                {/* Visible stages */}
                {visibleStages.map((stage, index) => (
                    <React.Fragment key={stage.id}>
                        <div className="flex items-center">
                            <div className={`
                                w-4 h-4 rounded-full flex items-center justify-center text-xs font-medium
                                ${stage.id === currentMajorStage
                                ? 'bg-[var(--color-primary)] text-white'
                                : stage.id < currentMajorStage
                                    ? 'bg-[var(--color-success)] text-white'
                                    : 'bg-[var(--color-background-alt)] text-[var(--color-border-strong)]'
                            }
                            `}>
                                {stage.id < currentMajorStage ? '✓' : stage.id}
                            </div>
                            <span className={`
                                ml-1 text-xs font-medium whitespace-nowrap
                                ${stage.id === currentMajorStage
                                ? 'text-[var(--color-primary)]'
                                : 'text-[var(--color-text)]'
                            }
                            `}>
                                {stage.name}
                            </span>
                        </div>
                        {index < visibleStages.length - 1 && (
                            <div className={`
                                flex-1 h-0.5 mx-1 min-w-[20px]
                                ${stage.id < currentMajorStage ? 'bg-[var(--color-success)]' : 'bg-[var(--color-background-alt)]'}
                            `} />
                        )}
                    </React.Fragment>
                ))}

                {/* Show dots for future stages if not visible */}
                {currentMajorStage + 2 < stageConfig.length && (
                    <>
                        <div className="h-0.5 w-2 bg-[var(--color-background-alt)] mx-1"></div>
                        <div className="flex items-center">
                            <div className="w-0.5 h-0.5 rounded-full bg-[var(--color-border)] mx-0.5"></div>
                            <div className="w-0.5 h-0.5 rounded-full bg-[var(--color-border)] mx-0.5"></div>
                            <div className="w-1 h-1 rounded-full bg-[var(--color-background-alt)] mx-0.5"></div>
                        </div>
                    </>
                )}
            </div>

            {/* Sub-stage Progress and Navigation */}
            <div className="flex items-center justify-between">
                {/* Previous Arrow */}
                <button
                    onClick={handlePrevious}
                    disabled={!effectiveCanGoPrevious}
                    className={`
                        w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold
                        ${effectiveCanGoPrevious
                        ? 'text-[var(--color-primary)] hover:bg-[var(--color-secondary)]/20 border border-[var(--color-primary)]'
                        : 'text-[var(--color-border)] cursor-not-allowed border border-[var(--color-border)]'
                    }
                    ${isDisabled ? 'opacity-50 cursor-wait' : ''}
                    `}
                    title={isDisabled ? 'Please wait one moment...' : ''}
                >
                    ←
                </button>

                {/* Current Sub-stage Info */}
                <div className="flex-1 mx-2">
                    <div className="text-center mb-0.5">
                        <span className="text-xs text-[var(--color-text)] font-medium">
                            {currentSubStageName}
                        </span>
                        <span className="text-xs text-[var(--color-border-strong)] ml-1">
                            ({currentSubStage}/{totalSubStages})
                        </span>
                    </div>
                    {/* Progress bar for substages */}
                    <div className="w-3/4 bg-[var(--color-background-alt)] rounded-full h-1 mx-auto">
                        <div
                            className="bg-[var(--color-primary)] h-1 rounded-full transition-all duration-300"
                            style={{ width: `${currentStageProgress}%` }}
                        />
                    </div>
                </div>

                {/* Next Arrow */}
                <button
                    onClick={handleAdvance}
                    disabled={!effectiveCanGoNext}
                    className={`
                        w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold
                        ${effectiveCanGoNext
                        ? 'text-[var(--color-primary)] hover:bg-[var(--color-secondary)]/20 border border-[var(--color-primary)]'
                        : 'text-[var(--color-border)] cursor-not-allowed border border-[var(--color-border)]'
                    }
                    ${isDisabled ? 'opacity-50 cursor-wait' : ''}
                    `}
                    title={isDisabled ? 'Please wait one moment...' : ''}
                >
                    →
                </button>
            </div>
        </div>
    );
}