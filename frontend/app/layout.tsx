import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Zero Vape SEO Platform',
  description: 'SEO management platform for Zero Vape',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
