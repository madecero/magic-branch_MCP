// GenerationProgress.tsx 
import { useState, useEffect } from 'react';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { GenerationStep } from '../utils/api';
import { Page } from '../types/page';
import { useSwipeable } from 'react-swipeable';

interface Props {
  step: GenerationStep;
}

const flipVariants = {
  initial: (direction: number) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
    scale: 0.8,
  }),
  animate: {
    x: 0,
    opacity: 1,
    scale: 1,
    transition: { 
      duration: 0.5, 
      ease: [0.23, 1, 0.32, 1] as const, // Custom bezier curve for smooth page turn
      x: { type: "spring" as const, stiffness: 300, damping: 30 },
    },
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -300 : 300,
    opacity: 0,
    scale: 0.8,
    transition: { 
      duration: 0.4, 
      ease: [0.76, 0, 0.24, 1] as const, // Different easing for exit
    },
  }),
};

export default function GenerationProgress({ step }: Props) {
  const [isReading, setIsReading] = useState(false);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [availablePages, setAvailablePages] = useState<Page[]>([]);
  const [direction, setDirection] = useState(0); // 1 for next (forward), -1 for prev (backward)

  useEffect(() => {
    if (step.availablePages) {
      const newPages = step.availablePages;
      if (newPages.length > availablePages.length) {
        toast.success(`New page ready! 🎉 (Page ${newPages.length})`, { duration: 2000 });
      }
      setAvailablePages(newPages);
    }
  }, [step.availablePages]);

  const getProgressPercentage = () => {
    switch (step.step) {
      case 'story': return 25;
      case 'cover': return 40;
      case 'pages': 
        if (step.currentPage && step.totalPages) {
          return 40 + (step.currentPage / step.totalPages) * 60;
        }
        return 60;
      case 'complete': return 100;
      default: return 0;
    }
  };

  const getStepIcon = () => {
    switch (step.step) {
      case 'story': return '📝';
      case 'cover': return '🎨';
      case 'pages': return '🖼️';
      case 'complete': return '🎉';
      default: return '⏳';
    }
  };

  const isComplete = step.step === 'complete';
  const canStartReading = isComplete; // Changed: only when fully complete

  // Swipe handlers (works on touch/mobile and mouse drag on web)
  const handlers = useSwipeable({
    onSwipedLeft: () => {
      if (currentPageIndex < fullPages.length - 1) {
        setDirection(1);
        setCurrentPageIndex(currentPageIndex + 1);
      }
    },
    onSwipedRight: () => {
      if (currentPageIndex > 0) {
        setDirection(-1);
        setCurrentPageIndex(currentPageIndex - 1);
      }
    },
    trackMouse: true, // Enables mouse drag on web
    preventScrollOnSwipe: true,
  });

  // Full pages including cover (only when complete)
  const fullPages: Page[] = isReading && step.coverImage && availablePages
    ? [{ text: '', image: step.coverImage }, ...availablePages]
    : [];

  // Reader View: Full-screen immersive with text below image, swipe-enabled
  if (isReading) {
    if (fullPages.length === 0) {
      return <div className="text-center p-8">Loading your story...</div>;
    }

    const currentPage = fullPages[currentPageIndex];
    const isCover = currentPageIndex === 0 && !currentPage.text;

    return (
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="relative min-h-screen flex flex-col overflow-hidden"
        {...handlers} // Attach swipe handlers to the whole view
      >
        {/* Dynamic Header */}
        <div className="absolute top-0 left-0 right-0 z-20 text-center space-y-2 px-4 py-4">
          {isCover ? (
            <h1 className="text-2xl font-bold text-gray-800 bg-white/80 rounded-lg py-2 px-4 inline-block">
              {step.title}
            </h1>
          ) : (
            <p className="text-sm text-gray-600 bg-white/80 rounded-lg py-1 px-3 inline-block">
              Page {currentPageIndex} of {fullPages.length - 1}
            </p>
          )}
        </div>

        {/* Page Content: Image with optional text below */}
        <AnimatePresence mode="wait">
          <motion.div 
            key={currentPage.image}
            custom={direction}
            variants={flipVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            className="flex-grow flex flex-col"
          >
            {/* Image Section - Full height for cover, fixed for pages */}
            <div className={`relative ${isCover ? 'flex-grow' : 'flex-shrink-0 h-[60vh]'}`}>
              <Image
                src={currentPage.image}
                alt={isCover ? 'Book Cover' : `Page ${currentPageIndex}`}
                fill
                className="object-cover"
              />
              {currentPage.image.includes('dummyimage') || currentPage.image.includes('placeholder') ? (
                <div className="absolute inset-0 flex items-center justify-center bg-white/70">
                  <motion.div 
                    animate={{ rotate: 360 }} 
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} 
                    className="text-4xl mr-2"
                  >
                    ✨
                  </motion.div>
                  <p className="text-blue-600">Conjuring image...</p>
                </div>
              ) : null}
            </div>
            
            {/* Text Section - Only if text exists */}
            {currentPage.text && (
              <motion.div 
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="p-6 bg-white text-gray-800 leading-relaxed text-lg overflow-auto"
              >
                {currentPage.text}
              </motion.div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Swipe Hint Footer - Only on cover, persistent */}
        {isCover && (
          <motion.div 
            initial={{ opacity: 1 }}
            className="absolute bottom-4 left-0 right-0 z-20 text-center"
          >
            <p className="text-sm text-gray-500 bg-white/80 rounded-lg py-1 px-3 inline-block shadow-sm">
              Swipe to turn the page
            </p>
          </motion.div>
        )}
      </motion.div>
    );
  }

  // Progress View (added cover preview under summary, moved pulsing above)
  return (
    <div className="max-w-lg mx-auto p-6 space-y-6">
      {/* Start Reading Button (always on top if ready) */}
      {canStartReading && (
        <div className="text-center sticky top-0 bg-white z-10 py-4 -mx-6 px-6 shadow-md">
          <button
            onClick={() => setIsReading(true)}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200 transform hover:scale-105 shadow-lg w-full"
          >
            📖 Read Your Complete Story!
          </button>
          <p className="text-sm text-green-600 font-medium mt-2">
            ✅ All {step.totalPages} pages are ready!
          </p>
        </div>
      )}

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
          style={{ width: `${getProgressPercentage()}%` }}
        />
      </div>
      
      {/* Current Step */}
      <div className="text-center space-y-4">
        <div className="text-4xl">{getStepIcon()}</div>
        <p className="text-lg font-medium text-gray-800">{step.message}</p>
      </div>

      {/* Pulsing Animation (moved above summary) */}
      {!isComplete && (
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-pulse flex space-x-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-200"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-400"></div>
          </div>
        </div>
      )}

      {/* Story Title & Summary with Cover Below */}
      {step.title && step.summary && (
        <div className="bg-blue-50 rounded-lg p-4 space-y-3">
          <h2 className="text-xl font-bold text-center text-gray-800">{step.title}</h2>
          <p className="text-gray-700 text-center leading-relaxed">{step.summary}</p>
          {step.coverImage && (
            <div className="relative h-64 mx-auto max-w-xs">
              <Image
                src={step.coverImage}
                alt="Book Cover"
                fill
                className="object-contain rounded-lg"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}