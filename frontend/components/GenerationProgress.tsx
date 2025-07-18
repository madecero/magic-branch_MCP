import { useState, useEffect } from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { GenerationStep } from '../utils/api';
import { Page } from '../types/page';

interface Props {
  step: GenerationStep;
}

export default function GenerationProgress({ step }: Props) {
  const [isReading, setIsReading] = useState(false);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [availablePages, setAvailablePages] = useState<Page[]>([]);

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
      case 'enticer': return 10;
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
      case 'enticer': return '✨';
      case 'story': return '📝';
      case 'cover': return '🎨';
      case 'pages': return '🖼️';
      case 'complete': return '🎉';
      default: return '⏳';
    }
  };

  const canStartReading = availablePages.length >= 3;
  const isComplete = step.step === 'complete';

  const funFacts = [
    "Did you know? Dragons love ice cream on hot days! 🐉🍦",
    "Fun fact: Unicorns can paint rainbows with their horns! 🦄🌈",
    "Magical tip: Fairies hide treasures in flower petals! 🧚‍♀️🌸",
    "Adventure alert: Pirates always share their gold with friends! 🏴‍☠️💰",
  ];

  const getRandomFunFact = () => funFacts[Math.floor(Math.random() * funFacts.length)];

  // Reader View (folded from StoryReader.tsx and StoryViewer.tsx)
  if (isReading) {
    if (availablePages.length === 0) {
      return <div className="text-center p-8">Loading your story...</div>;
    }

    const currentPage = availablePages[currentPageIndex];
    const canGoNext = currentPageIndex < availablePages.length - 1;
    const canGoPrev = currentPageIndex > 0;

    return (
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        className="max-w-2xl mx-auto p-4 space-y-6"
      >
        {/* Header */}
        <div className="text-center space-y-2">
          {step.title && <h1 className="text-2xl font-bold text-gray-800">{step.title}</h1>}
          <p className="text-sm text-gray-600">
            Page {currentPageIndex + 1} of {availablePages.length}
            {!isComplete && availablePages.length < (step.totalPages || 0) && (
              <span className="text-blue-600"> (More pages coming...)</span>
            )}
          </p>
        </div>

        {/* Page Content */}
        <motion.div 
          key={currentPage.image}
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          className="bg-white rounded-lg shadow-lg overflow-hidden"
        >
          {/* Page Image with Placeholder */}
          <div className="relative w-full h-80 bg-gray-100">
            <Image
              src={currentPage.image}
              alt={`Page ${currentPageIndex + 1}`}
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
          
          {/* Page Text */}
          <div className="p-6">
            <p className="text-gray-800 leading-relaxed text-lg">
              {currentPage.text}
            </p>
          </div>
        </motion.div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => setCurrentPageIndex(currentPageIndex - 1)}
            disabled={!canGoPrev}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              canGoPrev
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            ← Previous
          </button>

          <div className="flex space-x-2">
            {availablePages.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentPageIndex(index)}
                className={`w-3 h-3 rounded-full transition-all ${
                  index === currentPageIndex
                    ? 'bg-blue-600'
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
              />
            ))}
          </div>

          <button
            onClick={() => setCurrentPageIndex(currentPageIndex + 1)}
            disabled={!canGoNext}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              canGoNext
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Next →
          </button>
        </div>

        {/* Generation Status and Fun Facts */}
        {!isComplete && (
          <div className="text-center p-4 bg-blue-50 rounded-lg space-y-2">
            <p className="text-blue-700">
              🎨 Still creating more pages... Keep reading!
            </p>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-gray-600"
            >
              {getRandomFunFact()}
            </motion.p>
          </div>
        )}

        {/* Back to Overview Button (if needed) */}
        <div className="text-center">
          <button
            onClick={() => setIsReading(false)}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Overview
          </button>
        </div>
      </motion.div>
    );
  }

  // Progress View (before starting reading)
  return (
    <div className="max-w-lg mx-auto p-6 space-y-6">
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

      {/* Enticer */}
      {step.enticer && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border-l-4 border-purple-400">
          <p className="text-gray-700 text-center leading-relaxed font-medium">
            {step.enticer}
          </p>
        </div>
      )}

      {/* Story Title & Summary */}
      {step.title && step.summary && (
        <div className="bg-blue-50 rounded-lg p-4 space-y-3">
          <h2 className="text-xl font-bold text-center text-gray-800">{step.title}</h2>
          <p className="text-gray-700 text-center leading-relaxed">{step.summary}</p>
        </div>
      )}
      
      {/* Cover Image Preview */}
      {step.coverImage && (
        <div className="space-y-3">
          <p className="text-center text-sm font-medium text-gray-700">Your Book Cover</p>
          <div className="relative w-56 h-56 mx-auto rounded-lg overflow-hidden shadow-lg">
            <Image
              src={step.coverImage}
              alt="Book cover"
              fill
              className="object-cover"
            />
          </div>
        </div>
      )}

      {/* Start Reading Button */}
      {canStartReading && (
        <div className="text-center">
          {!isComplete ? (
            <>
              <button
                onClick={() => setIsReading(true)}
                className="bg-gradient-to-r from-green-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                🚀 Start Reading Your Story!
              </button>
              <p className="text-sm text-gray-600 mt-2">
                {availablePages.length} of {step.totalPages} pages ready
              </p>
            </>
          ) : (
            <div className="space-y-3">
              <button
                onClick={() => setIsReading(true)}
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                📖 Read Your Complete Story!
              </button>
              <p className="text-sm text-green-600 font-medium">
                ✅ All {step.totalPages} pages are ready!
              </p>
            </div>
          )}
        </div>
      )}
      
      {/* Pulsing Animation and Fun Fact */}
      {!isComplete && !canStartReading && (
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-pulse flex space-x-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-200"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-400"></div>
          </div>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-sm text-gray-600"
          >
            {getRandomFunFact()}
          </motion.p>
        </div>
      )}
    </div>
  );
}