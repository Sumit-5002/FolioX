import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "MF Portfolio X-Ray | AI Money Mentor",
  description:
    "Upload your CAMS statement and get your entire mutual fund portfolio analyzed in 10 seconds. True XIRR, expense drain, tax harvesting, goal probability — powered by AI.",
  keywords: "mutual fund, CAMS, XIRR, portfolio analysis, expense ratio, tax harvesting, India",
  openGraph: {
    title: "MF Portfolio X-Ray | AI Money Mentor",
    description: "Know the truth about your mutual fund returns. AI-powered portfolio X-Ray.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body className="bg-dark-900 text-white antialiased min-h-screen font-sans">
        {children}
      </body>
    </html>
  );
}
