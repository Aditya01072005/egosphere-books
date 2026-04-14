import { useState, useEffect, useCallback } from 'react';
import Navbar from '@/components/Navbar';
import BookCard from '@/components/BookCard';
import ScrapeModal from '@/components/ScrapeModal';
import { fetchBooks, fetchGenres } from '@/lib/api';

export default function Dashboard() {
  const [books, setBooks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [showScrape, setShowScrape] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const loadBooks = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (selectedGenre) params.genre = selectedGenre;
      const res = await fetchBooks(params);
      setBooks(res.data.books);
      setTotalCount(res.data.count);
    } catch {
      setBooks([]);
    } finally {
      setLoading(false);
    }
  }, [search, selectedGenre]);

  useEffect(() => {
    loadBooks();
  }, [loadBooks]);

  useEffect(() => {
    fetchGenres()
      .then((res) => setGenres(res.data.genres))
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Book Library</h1>
            <p className="text-gray-400 text-sm mt-1">{totalCount} books in database</p>
          </div>
          <button
            onClick={() => setShowScrape(true)}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium text-sm transition-colors self-start sm:self-auto"
          >
            🕷️ Scrape Books
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <input
            type="text"
            placeholder="Search by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
          />
          <select
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-indigo-500 text-sm min-w-[180px]"
          >
            <option value="">All Genres</option>
            {genres.map((g, i) => (
              <option key={`${g}-${i}`} value={g}>{g}</option>
            ))}
          </select>
        </div>

        {/* Book Grid */}
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="bg-gray-900 rounded-xl h-72 animate-pulse" />
            ))}
          </div>
        ) : books.length === 0 ? (
          <div className="text-center py-24">
            <p className="text-5xl mb-4">📚</p>
            <p className="text-gray-400 text-lg">No books found.</p>
            <p className="text-gray-600 text-sm mt-2">
              Click &quot;Scrape Books&quot; to populate the library.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </main>

      {showScrape && (
        <ScrapeModal
          onClose={() => setShowScrape(false)}
          onSuccess={loadBooks}
        />
      )}
    </div>
  );
}
