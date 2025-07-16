import axios from "axios";
import { Page } from "../types/page";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export interface GenerationStep {
  step: 'enticer' | 'story' | 'cover' | 'pages' | 'complete';
  message: string;
  enticer?: string;
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
  // Step 1: Generate enticer quickly while story generates in background
  onProgress({ step: 'enticer', message: 'Creating your magical adventure...' });
  
  // Start both calls simultaneously
  const [enticerRes, storyRes] = await Promise.all([
    API.post("/generate-enticer", payload),
    (() => {
      // Show enticer as soon as it's ready
      return API.post("/generate-enticer", payload).then(res => {
        onProgress({ 
          step: 'enticer', 
          message: 'Writing your full story...', 
          enticer: res.data.enticer 
        });
        // Now start the full story generation
        return API.post("/generate-story", payload);
      });
    })()
  ]);
  
  // Show story summary after story is generated
  onProgress({ 
    step: 'story', 
    message: 'Your story is ready! Creating your book cover...', 
    enticer: enticerRes.data.enticer,
    title: storyRes.data.title,
    summary: storyRes.data.summary 
  });
  
  // Step 2: Generate cover
  const coverRes = await API.post("/generate-cover", storyRes.data);
  
  onProgress({ 
    step: 'cover', 
    message: 'Book cover ready! Creating page illustrations...', 
    enticer: enticerRes.data.enticer,
    title: storyRes.data.title,
    summary: storyRes.data.summary,
    coverImage: coverRes.data.cover_image 
  });
  
  // Step 3: Generate page images progressively
  const pages = storyRes.data.story_pages;
  const finalPages: Page[] = [];
  const availablePages: Page[] = [];
  
  for (let i = 0; i < pages.length; i++) {
    onProgress({ 
      step: 'pages', 
      message: `Creating illustrations...`,
      enticer: enticerRes.data.enticer,
      title: storyRes.data.title,
      summary: storyRes.data.summary,
      coverImage: coverRes.data.cover_image,
      currentPage: i + 1,
      totalPages: pages.length,
      availablePages: [...availablePages]
    });
    
    const pageRes = await API.post("/generate-page-image", {
      text: pages[i],
      coverImage: coverRes.data.cover_image,
      pageIndex: i,
      character_descriptions: storyRes.data.character_descriptions,
      art_style: storyRes.data.art_style,
      context: storyRes.data.context
    });
    
    const newPage = {
      text: pages[i],
      image: pageRes.data.image_url
    };
    
    finalPages.push(newPage);
    availablePages.push(newPage);
    
    const canStartReading = availablePages.length >= 3;
    
    onProgress({ 
      step: 'pages', 
      message: canStartReading 
        ? `${availablePages.length >= pages.length ? 'Your story is complete!' : 'Keep reading while we finish up...'}`
        : `Almost ready to start reading...`,
      enticer: enticerRes.data.enticer,
      title: storyRes.data.title,
      summary: storyRes.data.summary,
      coverImage: coverRes.data.cover_image,
      currentPage: i + 1,
      totalPages: pages.length,
      availablePages: [...availablePages]
    });
  }
  
  onProgress({ 
    step: 'complete', 
    message: 'Your complete story is ready!',
    enticer: enticerRes.data.enticer,
    title: storyRes.data.title,
    summary: storyRes.data.summary,
    coverImage: coverRes.data.cover_image,
    pages: finalPages,
    availablePages: finalPages
  });
  
  return finalPages;
};