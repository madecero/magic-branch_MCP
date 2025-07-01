import axios from "axios";
import { Page } from "../types/page";

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
}): Promise<Page[]> => {
  const res = await API.post("/generate", payload);
  return res.data.pages; // assuming backend returns { pages: [...] }
};
