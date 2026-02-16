import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar"; // Assuming Navbar is compatible or I'll fix it if it breaks

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SocialGuard - Moderation Dashboard",
  description: "Multi-platform social media moderation tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="flex min-h-screen bg-slate-50/50">
          <div className="hidden border-r bg-gray-100/40 lg:block lg:w-64 fixed h-full z-10">
            <Sidebar className="h-full bg-slate-50" />
          </div>
          <div className="flex-1 flex flex-col lg:pl-64 transition-all duration-300">
            {/* Navbar could be here or in pages. Let's put it here for consistency if it's global */}
            {/* <Navbar />  -- Navbar seemed to be page-specific in original page.tsx, but usually global. 
                 Let's check if Navbar exists and is generic. 
                 In page.tsx it was imported. 
                 I'll add it here. */}
            <div className="flex-1 overflow-auto">
              {children}
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
