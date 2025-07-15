// api.ts
import axios from "axios";
import { StoryData } from "../types/story.ts"; // Updated type

// ✅ Update this if you're testing locally, or keep it pointed to Render
const API = axios.create({
  baseURL: "http://localhost:8000", // Local FastAPI backend
});

export const generateStory = async (payload: {
  name: string;
  gender: string;
  age: number;
  interests: string[];
  length: number;
}): Promise<StoryData> => {
  const res = await API.post("/generate", payload);
  return res.data; // Now returns { pages: [...], title: "...", cover_image: "..." } assuming backend updated
};