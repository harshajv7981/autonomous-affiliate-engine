import type { ReactNode } from 'react';
import './globals.css';

export const metadata = {
  title: 'Affiliate Engine Dashboard',
  description: 'Autonomous affiliate campaign management dashboard',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
