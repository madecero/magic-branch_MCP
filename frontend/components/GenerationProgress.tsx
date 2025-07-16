import Image from 'next/image';
import { GenerationStep } from '../utils/api';

interface Props {
  step: GenerationStep;
  onStartReading?: () => void;
}

export default function GenerationProgress({ step, onStartReading }: Props) {
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

  const canStartReading = step.availablePages && step.availablePages.length >= 3;
  const isComplete = step.step === 'complete';

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

      {/* Enticer - Shows first and hooks the user */}
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

      {/* Start Reading Button or Completion Message */}
      {canStartReading && onStartReading && (
        <div className="text-center">
          {!isComplete ? (
            <>
              <button
                onClick={onStartReading}
                className="bg-gradient-to-r from-green-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                🚀 Start Reading Your Story!
              </button>
              <p className="text-sm text-gray-600 mt-2">
                {step.availablePages!.length} of {step.totalPages} pages ready
              </p>
            </>
          ) : (
            <div className="space-y-3">
              <button
                onClick={onStartReading}
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
      
      {/* Pulsing Animation - only show when still generating and can't start reading */}
      {!isComplete && !canStartReading && (
        <div className="flex justify-center">
          <div className="animate-pulse flex space-x-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-200"></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animation-delay-400"></div>
          </div>
        </div>
      )}
    </div>
  );
}