import { useState } from "react";
import { generateStoryProgressive, GenerationStep } from "../utils/api";
import { Page } from "../types/page";
import GenerationProgress from "./GenerationProgress";

interface Props {
  onStoryGenerated: (pages: Page[]) => void;
}

export default function StoryForm({ onStoryGenerated }: Props) {
  const [name, setName] = useState("");
  const [gender, setGender] = useState("neutral");
  const [age, setAge] = useState(4);
  const [interests, setInterests] = useState("");
  const [length, setLength] = useState(5);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState<GenerationStep | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    
    try {
      const pages = await generateStoryProgressive(
        {
          name,
          gender,
          age,
          interests: interests.split(",").map(i => i.trim()),
          length,
        },
        (step) => setCurrentStep(step)
      );
      
      // Optionally call onStoryGenerated if needed for parent state, but we keep in progress UI
      onStoryGenerated(pages);
      // Do NOT setIsGenerating(false) - stay in GenerationProgress for seamless reader experience
    } catch (error) {
      console.error('Story generation failed:', error);
      setIsGenerating(false);
      setCurrentStep(null);
    }
  };

  // Always show GenerationProgress once generation starts
  if (isGenerating && currentStep) {
    return <GenerationProgress step={currentStep} />;
  }

  // Show initial form
  return (
    <div className="max-w-sm mx-auto p-6">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          ✨ Create Your Story
        </h1>
        <p className="text-gray-600 text-sm">
          Tell us about yourself and we'll create a magical personalized story!
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            What's your name?
          </label>
          <input
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your name"
            value={name}
            onChange={e => setName(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            I am a...
          </label>
          <select
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={gender}
            onChange={e => setGender(e.target.value)}
          >
            <option value="neutral">Prefer not to say</option>
            <option value="girl">Girl</option>
            <option value="boy">Boy</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            How old are you?
          </label>
          <input
            type="number"
            min="1"
            max="12"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Age"
            value={age}
            onChange={e => setAge(Number(e.target.value))}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            What do you love? (separate with commas)
          </label>
          <input
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="dinosaurs, rainbows, puppies"
            value={interests}
            onChange={e => setInterests(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Story length
          </label>
          <select
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={length}
            onChange={e => setLength(Number(e.target.value))}
          >
            {[3, 5, 7, 10].map(n => (
              <option key={n} value={n}>{n} Pages</option>
            ))}
          </select>
        </div>

        <button
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
          type="submit"
          disabled={isGenerating}
        >
          {isGenerating ? "Creating Magic..." : "Create My Story ✨"}
        </button>
      </form>
    </div>
  );
}