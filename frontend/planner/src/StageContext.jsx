// StageContext.jsx
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

// Create the context
const StageContext = createContext();

// Stage event types - these are the events your components can listen for
export const STAGE_EVENTS = {
  STAGE_CHANGED: 'stage:changed',
  STAGE_ADVANCED: 'stage:advanced',
  STAGE_RESET: 'stage:reset',
  MAJOR_STAGE_CHANGED: 'stage:major_changed'
};

// Your stage configuration - customize this to match your actual stages
const STAGE_CONFIG = [
  {
    id: 1,
    name: 'Getting Started',
    subStages: [
      'Tutorial',
      'Your Big Idea',
      'Working Title',
      'Genre & Flavor',
      'Main Vibe',
      'One-Sentence Pitch'
    ]
  },
  {
    id: 2,
    name: 'Worldbuilding Basics',
    subStages: [
      'Setting',
      'Time Period',
      'The Map',
      'The Environment',
      'Magic: Yes or No'
    ]
  },
  {
    id: 3,
    name: 'Worldbuilding Expanded',
    subStages: [
      'Magic Rules',
      'History Snapshot',
      'Groups & Cultures',
      'Government & Power',
      'Everyday Life',
      'Creatures',
      'Plants & Resources'
    ]
  },
  {
    id: 4,
    name: 'Characters',
    subStages: [
      'Your Hero',
      'What They Want',
      'What’s in Their Way',
      'Your Villain',
      'Why They Oppose',
      'Sidekick or Ally',
      'Other Important Characters',
      'Character Secrets'
    ]
  },
  {
    id: 5,
    name: 'Plot Basics',
    subStages: [
      'Choose a Story Shape',
      'Inciting Incident',
      'Turning Point #1',
      'Midpoint Twist',
      'Turning Point #2',
      'Climax',
      'Resolution'
    ]
  },
  {
    id: 6,
    name: 'Plot Expanded',
    subStages: [
      'Stakes',
      'Theme (Optional)',
      'Subplots',
      'Foreshadowing',
      'Scene List'
    ]
  },
  {
    id: 7,
    name: 'Writing Style',
    subStages: [
      'Point of View',
      'Tone',
      'Audience',
      'Length Goal',
      'Sample Paragraph'
    ]
  }
];

// Calculate linear stage mapping - adjust this to match your backend's expectations
const calculateLinearStage = (majorStage, subStage) => {
  const stagesBeforeCurrent = {
    1: 0,   // Getting Started begins at stage 0
    2: 6,   // Worldbuilding Basics starts after 6 stages
    3: 11,  // Worldbuilding Expanded starts after 11 stages
    4: 18,  // Characters starts after 18 stages
    5: 26,  // Plot Basics starts after 26 stages
    6: 33,  // Plot Expanded starts after 33 stages
    7: 38   // Writing Style starts after 38 stages
  };

  return stagesBeforeCurrent[majorStage] + subStage;
};

// Provider component that wraps your app
export function StageProvider({ children }) {
  // Core stage state
  const [currentMajorStage, setCurrentMajorStage] = useState(1);
  const [currentSubStage, setCurrentSubStage] = useState(1);
  const [totalSubStages, setTotalSubStages] = useState(STAGE_CONFIG[0].subStages.length);

  // Helper function to get current stage info
  const getCurrentStageInfo = useCallback(() => {
    const majorStageInfo = STAGE_CONFIG.find(stage => stage.id === currentMajorStage);
    return {
      majorStageInfo,
      currentStageName: majorStageInfo?.name || 'Unknown',
      currentSubStageName: majorStageInfo?.subStages[currentSubStage - 1] || 'Unknown',
      linearStage: calculateLinearStage(currentMajorStage, currentSubStage),
      isFirstStage: currentMajorStage === 1 && currentSubStage === 1,
      isLastStage: currentMajorStage === STAGE_CONFIG.length && currentSubStage === totalSubStages
    };
  }, [currentMajorStage, currentSubStage, totalSubStages]);

  // Broadcast stage change events
  const broadcastStageChange = useCallback((eventType, oldStage, newStage, additionalData = {}) => {
    const eventDetail = {
      oldStage: {
        major: oldStage.major,
        sub: oldStage.sub,
        linear: oldStage.linear
      },
      newStage: {
        major: newStage.major,
        sub: newStage.sub,
        linear: newStage.linear
      },
      majorStage: newStage.major,
      subStage: newStage.sub,
      linearStage: newStage.linear,
      stageName: STAGE_CONFIG.find(s => s.id === newStage.major)?.name,
      subStageName: STAGE_CONFIG.find(s => s.id === newStage.major)?.subStages[newStage.sub - 1],
      isNewMajorStage: oldStage.major !== newStage.major,
      timestamp: new Date().toISOString(),
      ...additionalData
    };

    // Dispatch the main stage change event
    window.dispatchEvent(new CustomEvent(eventType, { detail: eventDetail }));

    // If major stage changed, dispatch additional event
    if (eventDetail.isNewMajorStage) {
      window.dispatchEvent(new CustomEvent(STAGE_EVENTS.MAJOR_STAGE_CHANGED, { detail: eventDetail }));
    }

    // console.log(`🎯 Stage Event: ${eventType}`, eventDetail);
  }, []);

  // Main function to change stages
  const changeStage = useCallback((newMajorStage, newSubStage, eventType = STAGE_EVENTS.STAGE_CHANGED) => {
    const currentInfo = getCurrentStageInfo();

    // Validate the new stage
    const targetMajorStage = STAGE_CONFIG.find(stage => stage.id === newMajorStage);
    if (!targetMajorStage) {
      console.error(`Invalid major stage: ${newMajorStage}`);
      return false;
    }

    if (newSubStage < 1 || newSubStage > targetMajorStage.subStages.length) {
      console.error(`Invalid sub stage: ${newSubStage} for major stage ${newMajorStage}`);
      return false;
    }

    const oldStage = {
      major: currentMajorStage,
      sub: currentSubStage,
      linear: currentInfo.linearStage
    };

    const newStage = {
      major: newMajorStage,
      sub: newSubStage,
      linear: calculateLinearStage(newMajorStage, newSubStage)
    };

    // Update state
    setCurrentMajorStage(newMajorStage);
    setCurrentSubStage(newSubStage);
    setTotalSubStages(targetMajorStage.subStages.length);

    // Broadcast the change
    broadcastStageChange(eventType, oldStage, newStage);

    return true;
  }, [currentMajorStage, currentSubStage, getCurrentStageInfo, broadcastStageChange]);

  // Navigate to next stage
  const advanceStage = useCallback(() => {
    const currentMajor = STAGE_CONFIG.find(stage => stage.id === currentMajorStage);

    if (currentSubStage < currentMajor.subStages.length) {
      // Advance within current major stage
      return changeStage(currentMajorStage, currentSubStage + 1, STAGE_EVENTS.STAGE_CHANGED);
    } else if (currentMajorStage < STAGE_CONFIG.length) {
      // Move to next major stage
      return changeStage(currentMajorStage + 1, 1, STAGE_EVENTS.STAGE_CHANGED);
    }

    console.log('Already at the last stage');
    return false;
  }, [currentMajorStage, currentSubStage, changeStage]);

  // Navigate to previous stage
  const goToPreviousStage = useCallback(() => {
    if (currentSubStage > 1) {
      return changeStage(currentMajorStage, currentSubStage - 1);
    } else if (currentMajorStage > 1) {
      const prevMajor = STAGE_CONFIG.find(stage => stage.id === currentMajorStage - 1);
      return changeStage(currentMajorStage - 1, prevMajor.subStages.length);
    }

    console.log('Already at the first stage');
    return false;
  }, [currentMajorStage, currentSubStage, changeStage]);

  // Reset to beginning
  const resetStages = useCallback(() => {
    const currentInfo = getCurrentStageInfo();

    const oldStage = {
      major: currentMajorStage,
      sub: currentSubStage,
      linear: currentInfo.linearStage
    };

    // Reset to first stage
    setCurrentMajorStage(1);
    setCurrentSubStage(1);
    setTotalSubStages(STAGE_CONFIG[0].subStages.length);

    // Special reset event
    window.dispatchEvent(new CustomEvent(STAGE_EVENTS.STAGE_RESET, {
      detail: {
        oldStage,
        newStage: { major: 1, sub: 1, linear: 1 },
        message: 'Stages reset to beginning',
        timestamp: new Date().toISOString()
      }
    }));

    console.log('🔄 Stages reset to beginning');
  }, [currentMajorStage, currentSubStage, getCurrentStageInfo]);

  // Navigation helpers
  const canGoNext = useCallback(() => {
    const currentInfo = getCurrentStageInfo();
    return !currentInfo.isLastStage;
  }, [getCurrentStageInfo]);

  const canGoPrevious = useCallback(() => {
    const currentInfo = getCurrentStageInfo();
    return !currentInfo.isFirstStage;
  }, [getCurrentStageInfo]);

  // Calculate progress percentage
  const getOverallProgress = useCallback(() => {
    const totalStages = STAGE_CONFIG.reduce((sum, stage) => sum + stage.subStages.length, 0);
    const currentLinear = calculateLinearStage(currentMajorStage, currentSubStage);
    return Math.round((currentLinear / totalStages) * 100);
  }, [currentMajorStage, currentSubStage]);

  // Get stage progress within current major stage
  const getCurrentStageProgress = useCallback(() => {
    return Math.round((currentSubStage / totalSubStages) * 100);
  }, [currentSubStage, totalSubStages]);

  // Create the context value
  const contextValue = {
    // Current state
    currentMajorStage,
    currentSubStage,
    totalSubStages,

    // Stage configuration
    stageConfig: STAGE_CONFIG,

    // Computed values
    ...getCurrentStageInfo(),
    overallProgress: getOverallProgress(),
    currentStageProgress: getCurrentStageProgress(),

    // Navigation state
    canGoNext: canGoNext(),
    canGoPrevious: canGoPrevious(),

    // Actions
    changeStage,
    advanceStage,
    goToPreviousStage,
    resetStages,

    // Direct setters (for compatibility with your existing progress stepper)
    setCurrentMajorStage: (stage) => changeStage(stage, currentSubStage),
    setCurrentSubStage: (stage) => changeStage(currentMajorStage, stage),
    setTotalSubStages
  };

  return (
    <StageContext.Provider value={contextValue}>
      {children}
    </StageContext.Provider>
  );
}

// Hook to use the stage context
export const useStage = () => {
  const context = useContext(StageContext);
  if (!context) {
    throw new Error('useStage must be used within a StageProvider');
  }
  return context;
};

// Hook for listening to stage events
export const useStageEvents = (eventType, handler) => {
  useEffect(() => {
    if (typeof handler !== 'function') {
      console.error('useStageEvents: handler must be a function');
      return;
    }

    window.addEventListener(eventType, handler);

    return () => {
      window.removeEventListener(eventType, handler);
    };
  }, [eventType, handler]);
};

// Utility hook to get all stage events in one place
export const useAllStageEvents = (handlers) => {
  useStageEvents(STAGE_EVENTS.STAGE_CHANGED, handlers.onStageChanged || (() => {}));
  useStageEvents(STAGE_EVENTS.MAJOR_STAGE_CHANGED, handlers.onMajorStageChanged || (() => {}));
  useStageEvents(STAGE_EVENTS.STAGE_ADVANCED, handlers.onStageAdvanced || (() => {}));
  useStageEvents(STAGE_EVENTS.STAGE_RESET, handlers.onStageReset || (() => {}));
};

export default StageContext;