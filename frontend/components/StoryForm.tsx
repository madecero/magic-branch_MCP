// StoryForm.tsx
import { useState } from "react";
import { generateStory } from "../utils/api";
import { StoryData } from "../types/story.ts"; // Updated to return full story data

export default function StoryForm({ onStoryGenerated }: { onStoryGenerated: (data: StoryData) => void }) {
  const [name, setName] = useState("");
  const [gender, setGender] = useState("neutral");
  const [age, setAge] = useState(4);
  const [interests, setInterests] = useState("");
  const [length, setLength] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Please enter your child's name.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const data = await generateStory({
        name,
        gender,
        age,
        interests: interests.split(",").map(i => i.trim()).filter(i => i),
        length,
      });
      setLoading(false);
      onStoryGenerated(data);
    } catch (err) {
      setLoading(false);
      setError("Oops! Something went wrong. Please try again.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center text-blue-800">Create a Magical Bedtime Story</h2>
      <p className="text-center text-gray-600">Fill in the details to generate a personalized adventure!</p>
      
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Child's Name</label>
        <input
          id="name"
          className="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          placeholder="e.g., Alex"
          value={name}
          onChange={e => setName(e.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="gender" className="block text-sm font-medium text-gray-700">Gender</label>
        <select
          id="gender"
          className="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={gender}
          onChange={e => setGender(e.target.value)}
        >
          <option value="neutral">Prefer not to say</option>
          <option value="girl">Girl</option>
          <option value="boy">Boy</option>
        </select>
      </div>

      <div>
        <label htmlFor="age" className="block text-sm font-medium text-gray-700">Age</label>
        <input
          id="age"
          type="number"
          min="1"
          max="12"
          className="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          placeholder="e.g., 5"
          value={age}
          onChange={e => setAge(Number(e.target.value))}
          required
        />
      </div>

      <div>
        <label htmlFor="interests" className="block text-sm font-medium text-gray-700">Interests (comma-separated)</label>
        <input
          id="interests"
          className="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          placeholder="e.g., dinosaurs, princesses, space"
          value={interests}
          onChange={e => setInterests(e.target.value)}
        />
      </div>

      <div>
        <label htmlFor="length" className="block text-sm font-medium text-gray-700">Story Length</label>
        <select
          id="length"
          className="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={length}
          onChange={e => setLength(Number(e.target.value))}
        >
          {[3, 5, 7, 10].map(n => <option key={n} value={n}>{n} Pages</option>)}
        </select>
      </div>

      {error && <p className="text-red-500 text-center">{error}</p>}

      <button
        className="bg-blue-600 text-white px-4 py-2 rounded w-full hover:bg-blue-700 disabled:bg-blue-300"
        type="submit"
        disabled={loading}
      >
        {loading ? "Generating Your Story..." : "Generate Story"}
      </button>
    </form>
  );
}