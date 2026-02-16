'use client';

import { useEffect, useState } from "react";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { PlatformBreakdown } from "@/components/dashboard/PlatformBreakdown";
// We reuse the Navbar or just use header in layout. 
// Layout has Sidebar.
import { Navbar } from "@/components/layout/Navbar";

export default function DashboardPage() {
    const [stats, setStats] = useState({
        totalPosts: 0,
        totalComments: 0,
        hateCount: 0,
        activePlatforms: 0
    });

    const [platformStats, setPlatformStats] = useState<any[]>([]);

    useEffect(() => {
        // Fetch data from backend
        // Reusing the /load-existing endpoint which returns all data
        const fetchData = async () => {
            try {
                const res = await fetch("http://localhost:8000/load-existing");
                if (res.ok) {
                    const data = await res.json();
                    const results = data.results || [];

                    let totalPosts = results.length;
                    let totalComments = 0;
                    let hateCount = 0;

                    let linkedinPosts = 0;
                    let linkedinComments = 0;
                    let linkedinHate = 0;

                    let youtubeVideos = 0;
                    let youtubeComments = 0;
                    let youtubeHate = 0;

                    results.forEach((r: any) => {
                        totalComments += r.comment_count;
                        const hate = r.comments.filter((c: any) => c.label === 'hate' || c.label === 'toxic' || c.label === 'severe_toxic' || c.label === 'identity_hate').length;
                        hateCount += hate;

                        // Identify platform
                        // Simple heuristic: if post_url contains youtube, it's youtube. else linkedin.
                        // Or scrape_channel adds specific field, but currently we map to post_url.
                        if (r.post_url && (r.post_url.includes('youtube.com') || r.post_url.includes('youtu.be'))) {
                            youtubeVideos++;
                            youtubeComments += r.comment_count;
                            youtubeHate += hate;
                        } else {
                            linkedinPosts++;
                            linkedinComments += r.comment_count;
                            linkedinHate += hate;
                        }
                    });

                    let activePlatforms = 0;
                    if (linkedinPosts > 0) activePlatforms++;
                    if (youtubeVideos > 0) activePlatforms++;

                    setStats({
                        totalPosts,
                        totalComments,
                        hateCount,
                        activePlatforms
                    });

                    setPlatformStats([
                        {
                            platform: 'linkedin',
                            postsScraped: linkedinPosts,
                            commentsAnalyzed: linkedinComments,
                            hateCount: linkedinHate,
                            isActive: true // Always active in this demo
                        },
                        {
                            platform: 'youtube',
                            postsScraped: youtubeVideos,
                            commentsAnalyzed: youtubeComments,
                            hateCount: youtubeHate,
                            isActive: true
                        },
                        {
                            platform: 'instagram',
                            postsScraped: 0,
                            commentsAnalyzed: 0,
                            hateCount: 0,
                            isActive: false
                        },
                        {
                            platform: 'facebook',
                            postsScraped: 0,
                            commentsAnalyzed: 0,
                            hateCount: 0,
                            isActive: false
                        }
                    ]);
                }
            } catch (e) {
                console.error("Error fetching stats:", e);
            }
        };

        fetchData();
    }, []);

    return (
        <div className="flex flex-col h-full">
            <Navbar />
            <main className="p-6 lg:p-10 space-y-8 max-w-7xl mx-auto w-full">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Overview</h2>
                    <p className="text-muted-foreground">Global monitoring statistics across all platforms.</p>
                </div>

                <StatsCards
                    totalPosts={stats.totalPosts}
                    totalComments={stats.totalComments}
                    hateCount={stats.hateCount}
                    activePlatforms={stats.activePlatforms}
                />

                <div>
                    <h3 className="text-xl font-semibold tracking-tight mb-4">Platform Breakdown</h3>
                    <PlatformBreakdown stats={platformStats} />
                </div>
            </main>
        </div>
    );
}
