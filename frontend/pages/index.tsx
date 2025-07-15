// index.tsx
import { useState } from "react";
import StoryForm from "../components/StoryForm";
import StoryViewer from "../components/StoryViewer";
import { StoryData } from "../types/story.ts"; // New type

export default function Home() {
  const [storyData, setStoryData] = useState<StoryData | null>(null);

  const handleRestart = () => setStoryData(null);

  return (
    <div className="max-w-md mx-auto min-h-screen p-4 bg-gradient-to-b from-blue-100 to-purple-100">
      {!storyData ? (
        <StoryForm onStoryGenerated={setStoryData} />
      ) : (
        <StoryViewer data={storyData} onRestart={handleRestart} />
      )}
    </div>
  );
}
