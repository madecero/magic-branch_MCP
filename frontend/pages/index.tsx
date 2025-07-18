import StoryForm from "../components/StoryForm";

export default function Home() {
  return (
    <div className="max-w-md mx-auto min-h-screen p-4">
      <StoryForm onStoryGenerated={() => {}} />
    </div>
  );
}