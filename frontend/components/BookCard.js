import Link from 'next/link';

const SENTIMENT_COLORS = {
  Positive: 'text-green-400',
  Uplifting: 'text-green-400',
  Negative: 'text-red-400',
  Dark: 'text-red-400',
  Neutral: 'text-gray-400',
  Mysterious: 'text-purple-400',
};

function StarRating({ rating }) {
  const stars = Math.round(rating || 0);
  return (
    <span className="text-yellow-400 text-sm">
      {'★'.repeat(stars)}{'☆'.repeat(5 - stars)}
      <span className="text-gray-400 ml-1">({rating?.toFixed(1) || '0.0'})</span>
    </span>
  );
}

export default function BookCard({ book }) {
  const sentimentColor = SENTIMENT_COLORS[book.ai_sentiment] || 'text-gray-400';

  return (
    <Link href={`/books/${book.id}`}>
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden hover:border-indigo-500 hover:shadow-lg hover:shadow-indigo-900/20 transition-all cursor-pointer h-full flex flex-col">
        {/* Cover Image */}
        <div className="relative h-52 bg-gray-800 flex items-center justify-center overflow-hidden">
          {book.cover_image_url ? (
            <img
              src={book.cover_image_url}
              alt={book.title}
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="text-5xl">📖</span>
          )}
          {book.price && (
            <span className="absolute top-2 right-2 bg-indigo-600 text-white text-xs px-2 py-1 rounded-full font-semibold">
              {book.price}
            </span>
          )}
        </div>

        {/* Content */}
        <div className="p-4 flex flex-col flex-1 gap-2">
          <h3 className="font-semibold text-white text-sm leading-snug line-clamp-2">
            {book.title}
          </h3>

          <StarRating rating={book.rating} />

          <div className="flex flex-wrap gap-1 mt-1">
            {book.genre && (
              <span className="bg-gray-800 text-indigo-300 text-xs px-2 py-0.5 rounded-full">
                {book.genre}
              </span>
            )}
            {book.ai_genre && book.ai_genre !== book.genre && (
              <span className="bg-indigo-900/40 text-indigo-300 text-xs px-2 py-0.5 rounded-full">
                AI: {book.ai_genre}
              </span>
            )}
            {book.ai_sentiment && (
              <span className={`text-xs px-2 py-0.5 rounded-full bg-gray-800 ${sentimentColor}`}>
                {book.ai_sentiment}
              </span>
            )}
          </div>

          <p className="text-gray-500 text-xs mt-auto">
            {book.availability || ''}
          </p>
        </div>
      </div>
    </Link>
  );
}
