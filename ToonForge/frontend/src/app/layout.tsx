import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ToonForge',
  description: '2D flat-style animation studio for automatic dialogue scene generation',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
