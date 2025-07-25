import axios from "axios";
import { Page } from "../types/page";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export interface GenerationStep {
  step: 'story' | 'cover' | 'pages' | 'complete';
  message: string;
  title?: string;
  summary?: string;
  coverImage?: string;
  pages?: Page[];
  availablePages?: Page[];
  currentPage?: number;
  totalPages?: number;
}

export const generateStoryProgressive = async (
  payload: {
    name: string;
    gender: string;
    age: number;
    interests: string[];
    length: number;
  },
  onProgress: (step: GenerationStep) => void
): Promise<Page[]> => {
  // Step 1: Generate full story first (includes title, summary, pages)
  onProgress({ step: 'story', message: 'Writing your magical adventure...' });
  
  const storyRes = await API.post("/generate-story", payload);
  
  onProgress({ 
    step: 'story', 
    message: 'Your story is ready! Creating your book cover...', 
    title: storyRes.data.title,
    summary: storyRes.data.summary 
  });
  
  // Step 2: Generate cover
  const coverRes = await API.post("/generate-cover", storyRes.data);
  
  onProgress({ 
    step: 'cover', 
    message: 'Book cover ready! Creating page illustrations...', 
    title: storyRes.data.title,
    summary: storyRes.data.summary,
    coverImage: coverRes.data.cover_image 
  });
  
  // Step 3: Generate page images progressively and in parallel
  const pages = storyRes.data.story_pages;
  const finalPages: Page[] = [];
  let availablePages: Page[] = [];
  
  // Fire all page generation requests in parallel
  const pagePromises = pages.map((text: string, i: number) => 
    API.post("/generate-page-image", {
      text,
      coverImage: coverRes.data.cover_image,
      pageIndex: i,
      character_descriptions: storyRes.data.character_descriptions,
      art_style: storyRes.data.art_style,
      context: storyRes.data.context
    }).then(pageRes => {
      const newPage = {
        text,
        image: pageRes.data.image_url
      };
      finalPages.push(newPage);
      availablePages = [...availablePages, newPage].sort((a, b) => pages.indexOf(a.text) - pages.indexOf(b.text));
      
      onProgress({ 
        step: 'pages', 
        message: availablePages.length >= 3 
          ? `${availablePages.length >= pages.length ? 'Your story is complete!' : 'Keep reading while we finish up...'}` 
          : `Almost ready to start reading...`,
        title: storyRes.data.title,
        summary: storyRes.data.summary,
        coverImage: coverRes.data.cover_image,
        currentPage: availablePages.length,
        totalPages: pages.length,
        availablePages: [...availablePages]
      });
      
      return newPage;
    })
  );
  
  await Promise.all(pagePromises);
  
  onProgress({ 
    step: 'complete', 
    message: 'Your complete story is ready!',
    title: storyRes.data.title,
    summary: storyRes.data.summary,
    coverImage: coverRes.data.cover_image,
    pages: finalPages.sort((a, b) => pages.indexOf(a.text) - pages.indexOf(b.text)),
    availablePages: finalPages
  });
  
  return finalPages;
};