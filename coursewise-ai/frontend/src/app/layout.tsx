import type { Metadata } from 'next';
import './globals.css';
import Navbar from '../components/Navbar';

export const metadata: Metadata = {
  title: 'CourseWise AI | Personalized Course Content Summarizer',
  description: 'Turn dense technical material into clear, personalized learning content adapted to your knowledge level.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased text-slate-900 bg-slate-50 min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-200 bg-white py-6 mt-12 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>CourseWise AI &copy; {new Date().getFullYear()} — Academic Technical Content Summarizer</span>
            <span className="text-slate-400">Strict Hallucination Control &amp; Page Traceability</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
