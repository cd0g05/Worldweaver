import React, { useEffect } from 'react'
import { useStage } from '../StageContext.jsx'

export default function ProgressStepper({ isDisabled = false}) {
    // ✅ Get everything from context
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
        <div className="w-3/5 mx-auto bg-white px-4 py-2">
            {/* Major Stages Progress Bar */}
            <div className="flex items-center justify-center mb-2">
                {stageConfig.map((stage, index) => (
                    <React.Fragment key={stage.id}>
                        <div className="flex items-center">
                            <div className={`
                                w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium
                                ${stage.id === currentMajorStage
                                ? 'bg-[#7C3AED] text-white'
                                : stage.id < currentMajorStage
                                    ? 'bg-green-500 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }
                            `}>
                                {stage.id < currentMajorStage ? '✓' : stage.id}
                            </div>
                            <span className={`
                                ml-1.5 text-xs font-medium
                                ${stage.id === currentMajorStage
                                ? 'text-[#7C3AED]'
                                : 'text-[#1F2937]'
                            }
                            `}>
                                {stage.name}
                            </span>
                        </div>
                        {index < stageConfig.length - 1 && (
                            <div className={`
                                flex-1 h-0.5 mx-2 min-w-[30px]
                                ${stage.id < currentMajorStage ? 'bg-green-500' : 'bg-gray-200'}
                            `} />
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* Sub-stage Progress and Navigation */}
            <div className="flex items-center justify-between">
                {/* Previous Arrow */}
                <button
                    onClick={handlePrevious}
                    disabled={!effectiveCanGoPrevious}
                    className={`
                        w-10 h-10 rounded-full flex items-center justify-center text-xl font-bold
                        ${effectiveCanGoPrevious
                        ? 'text-[#7C3AED] hover:bg-purple-50 border border-[#7C3AED]'
                        : 'text-gray-300 cursor-not-allowed border border-gray-200'
                    }
                    ${isDisabled ? 'opacity-50 cursor-wait' : ''}
                    `}
                    title={isDisabled ? 'Please wait one moment...' : ''}
                >
                    ←
                </button>

                {/* Current Sub-stage Info */}
                <div className="flex-1 mx-3">
                    <div className="text-center mb-1">
                        <span className="text-sm text-[#1F2937] font-medium">
                            {currentSubStageName}
                        </span>
                        <span className="text-xs text-gray-500 ml-2">
                            ({currentSubStage} of {totalSubStages}) - {Math.round(currentStageProgress)}%
                        </span>
                    </div>
                    {/* Progress bar for substages */}
                    <div className="w-1/2 bg-gray-200 rounded-full h-1.5 mx-auto">
                        <div
                            className="bg-[#7C3AED] h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${currentStageProgress}%` }}
                        />
                    </div>
                </div>

                {/* Next Arrow */}
                <button
                    onClick={handleAdvance}
                    disabled={!effectiveCanGoNext}
                    className={`
                        w-10 h-10 rounded-full flex items-center justify-center text-xl font-bold
                        ${effectiveCanGoNext
                        ? 'text-[#7C3AED] hover:bg-purple-50 border border-[#7C3AED]'
                        : 'text-gray-300 cursor-not-allowed border border-gray-200'
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