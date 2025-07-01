import { useState } from "react";
import { generateStory } from "../utils/api";
import { Page } from "../types/page";

export default function StoryForm({ onStoryGenerated }: { onStoryGenerated: (pages: Page[]) => void }) {
  const [name, setName] = useState("");
  const [gender, setGender] = useState("neutral");
  const [age, setAge] = useState(4);
  const [interests, setInterests] = useState("");
  const [length, setLength] = useState(5);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const pages = await generateStory({
      name,
      gender,
      age,
      interests: interests.split(",").map(i => i.trim()),
      length,
    });
    setLoading(false);
    onStoryGenerated(pages);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        className="w-full p-2 border rounded"
        placeholder="Child's Name"
        value={name}
        onChange={e => setName(e.target.value)}
      />

      <select
        className="w-full p-2 border rounded"
        value={gender}
        onChange={e => setGender(e.target.value)}
      >
        <option value="neutral">Prefer not to say</option>
        <option value="girl">Girl</option>
        <option value="boy">Boy</option>
      </select>

      <input
        type="number"
        className="w-full p-2 border rounded"
        placeholder="Age"
        value={age}
        onChange={e => setAge(Number(e.target.value))}
      />
      <input
        className="w-full p-2 border rounded"
        placeholder="Interests (comma-separated)"
        value={interests}
        onChange={e => setInterests(e.target.value)}
      />
      <select
        className="w-full p-2 border rounded"
        value={length}
        onChange={e => setLength(Number(e.target.value))}
      >
        {[3, 5, 7, 10].map(n => <option key={n} value={n}>{n} Pages</option>)}
      </select>
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded w-full"
        type="submit"
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate Story"}
      </button>
    </form>
  );
}
