import axios from "axios";
import { Page } from "../types/page";

const API = axios.create({
  baseURL: "http://localhost:8000", // Local backend URL for development
});

export const generateStory = async (payload: {
  name: string;
  gender: string;
  age: number;
  interests: string[];
  length: number;
}): Promise<Page[]> => {
  const res = await API.post("/generate", payload);
  return res.data.pages;
};