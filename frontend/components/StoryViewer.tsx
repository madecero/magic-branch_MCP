// StoryViewer.tsx
import { useState } from "react";
import Image from "next/image";
import { StoryData } from "../types/story.ts"; // New type including title and cover

export default function StoryViewer({ data, onRestart }: { data: StoryData; onRestart: () => void }) {
  const { title = "Your Magical Story", cover_image = "", pages } = data;
  const [index, setIndex] = useState(-1); // Start at -1 for cover
  const isCover = index === -1;
  const currentPage = isCover ? { text: title, image: cover_image || pages[0]?.image } : pages[index];

  const next = () => setIndex(i => Math.min(i + 1, pages.length - 1));
  const prev = () => setIndex(i => Math.max(i - 1, -1));

  return (
    <div className="text-center space-y-6 bg-white p-6 rounded-lg shadow-md min-h-screen flex flex-col justify-between">
      <h2 className="text-2xl font-bold text-blue-800">{title}</h2>
      
      <div className="relative w-full h-80 mx-auto rounded-lg overflow-hidden shadow-inner">
        <Image
          src={currentPage.image}
          alt={isCover ? "Story Cover" : `Page ${index + 1} illustration`}
          layout="fill"
          objectFit="contain"
          className="rounded"
        />
      </div>
      
      <p className="text-lg text-gray-800 italic">{isCover ? "Once upon a time..." : currentPage.text}</p>
      
      <div className="flex justify-between items-center">
        <button 
          onClick={prev} 
          className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 disabled:opacity-50" 
          disabled={index === -1}
          aria-label="Previous Page"
        >
          ⬅ Back
        </button>
        
        <span className="text-gray-600">
          {isCover ? "Cover" : `Page ${index + 1} of ${pages.length}`}
        </span>
        
        <button 
          onClick={next} 
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700" 
          aria-label={index === pages.length - 1 ? "Finish Story" : "Next Page"}
        >
          {index === pages.length - 1 ? "The End" : "Next ➡"}
        </button>
      </div>
      
      {index === pages.length - 1 && (
        <button 
          onClick={onRestart} 
          className="bg-purple-600 text-white px-4 py-2 rounded w-full mt-4 hover:bg-purple-700"
        >
          Generate Another Story
        </button>
      )}
    </div>
  );
}