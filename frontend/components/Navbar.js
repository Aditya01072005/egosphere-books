import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Navbar() {
  const router = useRouter();

  const links = [
    { href: '/', label: 'Dashboard' },
    { href: '/qa', label: 'Q&A' },
  ];

  return (
    <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
      <Link href="/" className="text-xl font-bold text-indigo-400 tracking-wide">
        📚 EgoSphere Books
      </Link>
      <div className="flex gap-6">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`text-sm font-medium transition-colors ${
              router.pathname === link.href
                ? 'text-indigo-400 border-b-2 border-indigo-400 pb-0.5'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
