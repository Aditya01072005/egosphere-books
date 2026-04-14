import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import BookCard from '@/components/BookCard';
import { fetchBookDetail, fetchRecommendations } from '@/lib/api';

function Badge({ label, value, color = 'indigo' }) {
  const colors = {
    indigo: 'bg-indigo-900/40 text-indigo-300 border-indigo-700',
    green: 'bg-green-900/40 text-green-300 border-green-700',
    purple: 'bg-purple-900/40 text-purple-300 border-purple-700',
    yellow: 'bg-yellow-900/40 text-yellow-300 border-yellow-700',
  };
  return (
    <div className={`border rounded-xl px-4 py-3 ${colors[color]}`}>
      <p className="text-xs opacity-70 mb-0.5">{label}</p>
      <p className="font-semibold text-sm">{value || '—'}</p>
    </div>
  );
}

export default function BookDetail() {
  const router = useRouter();
  const { id } = router.query;

  const [book, setBook] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([fetchBookDetail(id), fetchRecommendations(id)])
      .then(([bookRes, recRes]) => {
        setBook(bookRes.data);
        setRecommendations(recRes.data.recommendations);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 py-12">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-800 rounded w-1/2" />
            <div className="h-4 bg-gray-800 rounded w-1/3" />
            <div className="h-48 bg-gray-800 rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-gray-950">
        <Navbar />
        <div className="text-center py-24 text-gray-400">Book not found.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">

        {/* Back */}
        <Link href="/" className="text-indigo-400 hover:text-indigo-300 text-sm mb-6 inline-block">
          ← Back to Library
        </Link>

        {/* Book Header */}
        <div className="flex flex-col md:flex-row gap-8 mb-10">
          <div className="flex-shrink-0">
            {book.cover_image_url ? (
              <img
                src={book.cover_image_url}
                alt={book.title}
                className="w-48 h-64 object-cover rounded-xl shadow-2xl"
              />
            ) : (
              <div className="w-48 h-64 bg-gray-800 rounded-xl flex items-center justify-center text-6xl">
                📖
              </div>
            )}
          </div>

          <div className="flex-1">
            <h1 className="text-3xl font-bold text-white mb-2">{book.title}</h1>
            {book.author && book.author !== 'Unknown' && (
              <p className="text-gray-400 mb-3">by {book.author}</p>
            )}

            {/* Rating */}
            <div className="flex items-center gap-2 mb-4">
              <span className="text-yellow-400 text-lg">
                {'★'.repeat(Math.round(book.rating || 0))}
                {'☆'.repeat(5 - Math.round(book.rating || 0))}
              </span>
              <span className="text-gray-400 text-sm">
                {book.rating?.toFixed(1)} / 5.0
              </span>
            </div>

            {/* Badges */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              <Badge label="Genre" value={book.genre} color="indigo" />
              <Badge label="Price" value={book.price} color="green" />
              <Badge label="Availability" value={book.availability} color="yellow" />
              <Badge label="AI Sentiment" value={book.ai_sentiment} color="purple" />
            </div>

            {/* Book URL */}
            <a
              href={book.book_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-400 hover:text-indigo-300 text-sm underline"
            >
              View on books.toscrape.com ↗
            </a>
          </div>
        </div>

        {/* Description */}
        {book.description && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-3">Description</h2>
            <p className="text-gray-300 leading-relaxed text-sm">{book.description}</p>
          </section>
        )}

        {/* AI Insights */}
        <section className="mb-10">
          <h2 className="text-lg font-semibold text-white mb-4">🤖 AI Insights</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Summary */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h3 className="text-indigo-400 font-medium text-sm mb-2">📝 AI Summary</h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                {book.ai_summary || 'Not generated yet.'}
              </p>
            </div>
            {/* Genre + Sentiment */}
            <div className="space-y-4">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <h3 className="text-purple-400 font-medium text-sm mb-2">🏷️ AI Genre Classification</h3>
                <p className="text-gray-300 text-sm">{book.ai_genre || 'Not classified yet.'}</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <h3 className="text-green-400 font-medium text-sm mb-2">💬 Sentiment Analysis</h3>
                <p className="text-gray-300 text-sm">{book.ai_sentiment || 'Not analyzed yet.'}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold text-white mb-4">
              📚 If you liked this, you&apos;ll also like...
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
              {recommendations.map((rec) => (
                <BookCard key={rec.id} book={rec} />
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
