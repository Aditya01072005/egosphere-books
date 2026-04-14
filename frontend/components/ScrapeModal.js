import { useState } from 'react';
import { triggerScrape } from '@/lib/api';

export default function ScrapeModal({ onClose, onSuccess }) {
  const [pages, setPages] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleScrape = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await triggerScrape(pages);
      setResult(res.data);
      onSuccess();
    } catch (e) {
      setError(e.response?.data?.error || 'Scraping failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <h2 className="text-lg font-bold text-white mb-4">🕷️ Scrape Books</h2>
        <p className="text-gray-400 text-sm mb-4">
          Scrapes books.toscrape.com and generates AI insights + embeddings.
        </p>

        <label className="block text-sm text-gray-300 mb-1">Number of pages to scrape</label>
        <input
          type="number"
          min={1}
          max={50}
          value={pages}
          onChange={(e) => setPages(Number(e.target.value))}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white mb-4 focus:outline-none focus:border-indigo-500"
        />

        {error && <p className="text-red-400 text-sm mb-3">{error}</p>}

        {result && (
          <div className="bg-green-900/30 border border-green-700 rounded-lg p-3 mb-4 text-sm text-green-300">
            ✅ Done! Scraped {result.scraped} books, {result.new_books_added} new added.
          </div>
        )}

        <div className="flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Close
          </button>
          <button
            onClick={handleScrape}
            disabled={loading}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm rounded-lg font-medium transition-colors"
          >
            {loading ? 'Scraping...' : 'Start Scraping'}
          </button>
        </div>
      </div>
    </div>
  );
}
