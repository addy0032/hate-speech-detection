'use client';

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { ContentCard } from "@/components/dashboard/ContentCard";
import { Navbar } from "@/components/layout/Navbar";
import { Platform } from "@/components/dashboard/PlatformIcon";
import { Loader2 } from "lucide-react";

interface ScrapeResult {
    post_url: string;
    comment_count: number;
    comments: any[];
}

function ResultsContent() {
    const searchParams = useSearchParams();
    const platformParam = searchParams.get('platform');

    const [results, setResults] = useState<ScrapeResult[]>([]);
    const [loading, setLoading] = useState(true);
    const [activePlatform, setActivePlatform] = useState<Platform | 'all'>((platformParam as Platform) || 'all');

    useEffect(() => {
        setActivePlatform((platformParam as Platform) || 'all');
    }, [platformParam]);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const res = await fetch("http://localhost:8000/load-existing");
                if (res.ok) {
                    const data = await res.json();
                    setResults(data.results || []);
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const filteredResults = results.filter(r => {
        // Heuristic for platform detection
        const isYoutube = r.post_url.includes('youtube.com') || r.post_url.includes('youtu.be');
        const isInstagram = r.post_url.includes('instagram.com');
        const itemPlatform: Platform = isYoutube ? 'youtube' : isInstagram ? 'instagram' : 'linkedin';

        if (activePlatform === 'all') return true;
        return itemPlatform === activePlatform;
    });

    return (
        <main className="p-6 lg:p-10 space-y-8 max-w-7xl mx-auto w-full">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Results</h2>
                    <p className="text-muted-foreground">
                        Viewing {activePlatform === 'all' ? 'all' : activePlatform} content.
                    </p>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center p-12">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {filteredResults.length > 0 ? filteredResults.map((res, i) => {
                        const isYoutube = res.post_url.includes('youtube.com') || res.post_url.includes('youtu.be');
                        const isInstagram = res.post_url.includes('instagram.com');
                        const platform = isYoutube ? 'youtube' : isInstagram ? 'instagram' : 'linkedin';

                        // Calculate hate count
                        const hateCount = res.comments.filter((c: any) => c.label === 'hate' || c.label === 'toxic').length;
                        const safeCount = res.comment_count - hateCount;

                        return (
                            <ContentCard
                                key={i}
                                platform={platform}
                                url={res.post_url}
                                commentCount={res.comment_count}
                                hateCount={hateCount}
                                safeCount={safeCount}
                                title={res.post_url}
                            />
                        );
                    }) : (
                        <div className="col-span-full text-center p-12 text-muted-foreground">
                            No results found. Start a task to see data here.
                        </div>
                    )}
                </div>
            )}
        </main>
    );
}

export default function ResultsPage() {
    return (
        <div className="flex flex-col h-full">
            <Navbar />
            <Suspense fallback={<div className="flex justify-center p-12"><Loader2 className="h-8 w-8 animate-spin" /></div>}>
                <ResultsContent />
            </Suspense>
        </div>
    );
}
