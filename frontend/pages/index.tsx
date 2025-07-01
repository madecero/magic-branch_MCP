import { useState } from "react";
import StoryForm from "../components/StoryForm";
import StoryViewer from "../components/StoryViewer";
import { Page } from "../types/page";

export default function Home() {
  const [pages, setPages] = useState<Page[]>([]);

  return (
    <div className="max-w-md mx-auto min-h-screen p-4">
      {!pages.length && <StoryForm onStoryGenerated={setPages} />}
      {pages.length > 0 && <StoryViewer pages={pages} />}
    </div>
  );
}

