import { useState, useEffect } from 'react';
import Image from 'next/image';
import { Page } from '../types/page';

interface Props {
  pages: Page[];
  coverImage?: string;
  title?: string;
  isGenerationComplete: boolean;
}

export default function StoryReader({ pages, coverImage, title, isGenerationComplete }: Props) {
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [availablePages, setAvailablePages] = useState<Page[]>([]);

  useEffect(() => {
    setAvailablePages(pages);
  }, [pages]);

  const canGoNext = currentPageIndex < availablePages.length - 1;
  const canGoPrev = currentPageIndex > 0;

  const handleNext = () => {
    if (canGoNext) {
      setCurrentPageIndex(currentPageIndex + 1);
    }
  };

  const handlePrev = () => {
    if (canGoPrev) {
      setCurrentPageIndex(currentPageIndex - 1);
    }
  };

  if (availablePages.length === 0) {
    return <div className="text-center p-8">Loading your story...</div>;
  }

  const currentPage = availablePages[currentPageIndex];

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        {title && <h1 className="text-2xl font-bold text-gray-800">{title}</h1>}
        <p className="text-sm text-gray-600">
          Page {currentPageIndex + 1} of {availablePages.length}
          {!isGenerationComplete && availablePages.length < pages.length && (
            <span className="text-blue-600"> (More pages coming...)</span>
          )}
        </p>
      </div>

      {/* Page Content */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Page Image */}
        <div className="relative w-full h-80 bg-gray-100">
          <Image
            src={currentPage.image}
            alt={`Page ${currentPageIndex + 1}`}
            fill
            className="object-cover"
          />
        </div>
        
        {/* Page Text */}
        <div className="p-6">
          <p className="text-gray-800 leading-relaxed text-lg">
            {currentPage.text}
          </p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrev}
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
          onClick={handleNext}
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

      {/* Generation Status */}
      {!isGenerationComplete && (
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <p className="text-blue-700">
            🎨 Still creating more pages... Keep reading!
          </p>
        </div>
      )}
    </div>
  );
}