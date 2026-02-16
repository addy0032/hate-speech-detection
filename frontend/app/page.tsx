'use client';

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { StatusCard } from "@/components/dashboard/StatusCard";
import { PostCard } from "@/components/dashboard/PostCard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Play, Loader2 } from "lucide-react";

// Types
interface ScrapeResult {
  post_url: string;
  comment_count: number;
  comments: any[];
}

interface ScrapeStatus {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: string[];
  error?: string;
  results?: ScrapeResult[];
}

export default function Dashboard() {
  const [urls, setUrls] = useState("");
  const [days, setDays] = useState(30);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<ScrapeStatus | null>(null);
  const [allResults, setAllResults] = useState<ScrapeResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Helper to load all existing data
  const fetchExistingData = async () => {
    try {
      const res = await fetch("http://localhost:8000/load-existing");
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
        if (data.results) {
          setAllResults(data.results);
        }
        setTaskId(data.task_id);
      }
    } catch (e) {
      console.log("No existing data found or backend not ready");
    }
  };

  // Polling logic
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (taskId && taskId !== "existing_data" && status?.status !== "completed" && status?.status !== "failed") {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://localhost:8000/status/${taskId}`);
          if (res.ok) {
            const data: ScrapeStatus = await res.json();

            if (data.results && data.results.length > 0) {
              setAllResults(prev => {
                const newMap = new Map(prev.map(p => [p.post_url, p]));
                data.results?.forEach(r => newMap.set(r.post_url, r));
                return Array.from(newMap.values());
              });
            }

            if (data.status === "completed") {
              setIsLoading(false);
              clearInterval(interval);
              setStatus(data);
              await fetchExistingData();
            } else if (data.status === "failed") {
              setStatus(data);
              setIsLoading(false);
              clearInterval(interval);
            } else {
              setStatus(data);
            }
          }
        } catch (e) { console.error(e); }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [taskId, status?.status]);

  // Load existing data on mount
  useEffect(() => {
    fetchExistingData();
  }, []);

  const handleScrape = async () => {
    if (!urls.trim()) return;
    setIsLoading(true);
    setStatus(null);
    setTaskId(null);

    const urlList = urls.split("\n").map(u => u.trim()).filter(u => u.length > 0);

    try {
      const res = await fetch("http://localhost:8000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls: urlList, days: days }),
      });
      if (res.ok) {
        const data = await res.json();
        setTaskId(data.task_id);
        setStatus(data);
      } else {
        setIsLoading(false);
        alert("Failed to start task");
      }
    } catch (e) {
      console.error(e);
      setIsLoading(false);
      alert("Error connecting to backend");
    }
  };

  const handleDownload = () => {
    if (taskId) window.location.href = `http://localhost:8000/export/${taskId}`;
  };

  // Calculate stats
  const totalPosts = allResults.length;
  const totalComments = allResults.reduce((acc, curr) => acc + curr.comment_count, 0);
  const hateCount = allResults.reduce((acc, curr) =>
    acc + curr.comments.filter((c: any) => c.label === "hate" || c.label === "toxic").length, 0
  );
  const toxicCount = 0; // Merged with hate for now or calculate separately if label distinguishes

  return (
    <div className="flex min-h-screen bg-slate-50/50">
      {/* Sidebar */}
      <div className="hidden border-r bg-gray-100/40 lg:block lg:w-64">
        <Sidebar className="h-full bg-slate-50" />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Navbar />

        <main className="flex-1 p-6 lg:p-10 space-y-8 max-w-7xl mx-auto w-full">

          {/* Header */}
          <div className="flex justify-between items-end">
            <div className="space-y-1">
              <h2 className="text-3xl font-bold tracking-tight">Scraper Dashboard</h2>
              <p className="text-muted-foreground">
                Manage scraping tasks and analyze comments for hate speech.
              </p>
            </div>
          </div>

          {/* Stats */}
          <StatsCards
            totalPosts={totalPosts}
            totalComments={totalComments}
            hateCount={hateCount}
            toxicCount={toxicCount}
          />

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">

            {/* Input Section */}
            <Card className="col-span-4 rounded-xl shadow-sm border-slate-200">
              <CardHeader>
                <CardTitle>New Scraping Task</CardTitle>
                <CardDescription>
                  Enter LinkedIn Post or Page URLs below.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      Target URLs
                    </label>
                    <span className="text-xs text-muted-foreground">
                      One URL per line
                    </span>
                  </div>
                  <Textarea
                    value={urls}
                    onChange={(e) => setUrls(e.target.value)}
                    placeholder="https://www.linkedin.com/school/..."
                    className="font-mono text-sm min-h-[120px] bg-slate-50 focus:bg-white transition-colors"
                    disabled={isLoading}
                  />
                  <p className="text-[0.8rem] text-muted-foreground">
                    Supports individual post URLs and company/school page URLs (e.g., .../posts).
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none">
                    Lookback Period (Days)
                  </label>
                  <Input
                    type="number"
                    value={days}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDays(Number(e.target.value))}
                    min={1}
                    className="max-w-[150px]"
                    disabled={isLoading}
                  />
                  <p className="text-[0.8rem] text-muted-foreground">
                    How many days back to scrape posts from feeds.
                  </p>
                </div>

                <div className="flex justify-end">
                  <Button
                    onClick={handleScrape}
                    disabled={isLoading || !urls.trim()}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md transition-all rounded-lg px-6"
                    size="lg"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4 fill-current" />
                        Start Scraping
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Status / Logs */}
            <div className="col-span-3">
              <StatusCard
                status={status?.status || "idle"}
                progress={status?.progress || []}
                onDownload={handleDownload}
              />
            </div>
          </div>

          {/* Results Grid */}
          {allResults.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold tracking-tight">Results Preview</h3>
              </div>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {allResults.map((res, i) => (
                  <PostCard
                    key={`${res.post_url}-${i}`}
                    postUrl={res.post_url}
                    comments={res.comments}
                    index={i + 1}
                  />
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
