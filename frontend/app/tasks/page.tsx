'use client';

import { useState, useEffect } from "react";
import { PlatformTaskForm } from "@/components/dashboard/PlatformTaskForm";
import { StatusCard } from "@/components/dashboard/StatusCard"; // Assuming this exists from original page.tsx, need to check or recreate
// I need to check StatusCard. If it was in components/dashboard/StatusCard.tsx I should read it or import it.
// Step 18 showed `import { StatusCard } from "@/components/dashboard/StatusCard";` in page.tsx 
// so it exists.

import { Navbar } from "@/components/layout/Navbar";
import { Platform } from "@/components/dashboard/PlatformIcon";

// Types from page.tsx
interface ScrapeStatus {
    task_id: string;
    status: "pending" | "processing" | "completed" | "failed";
    progress: string[];
    error?: string;
    results?: any[];
}

export default function TasksPage() {
    const [projectId, setProjectId] = useState<string | null>(null); // Not used yet?
    const [taskId, setTaskId] = useState<string | null>(null);
    const [status, setStatus] = useState<ScrapeStatus | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    // Poll for status
    useEffect(() => {
        let interval: NodeJS.Timeout;
        // We poll /status/{taskId} which works for both platforms
        if (taskId && status?.status !== "completed" && status?.status !== "failed") {
            interval = setInterval(async () => {
                try {
                    const res = await fetch(`http://localhost:8000/status/${taskId}`);
                    if (res.ok) {
                        const data: ScrapeStatus = await res.json();
                        setStatus(data);
                        if (data.status === "completed" || data.status === "failed") {
                            setIsLoading(false);
                            clearInterval(interval);
                        }
                    }
                } catch (e) { console.error(e); }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [taskId, status?.status]);

    const handleStartScrape = async (platform: Platform, urls: string[], days: number) => {
        setIsLoading(true);
        setStatus(null);
        setTaskId(null);

        const endpoint = platform === 'youtube' ? 'http://localhost:8000/scrape/youtube' : 'http://localhost:8000/scrape';

        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ urls: urls, days: days }),
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

    return (
        <div className="flex flex-col h-full">
            <Navbar />
            <main className="p-6 lg:p-10 space-y-8 max-w-7xl mx-auto w-full">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Scraping Tasks</h2>
                    <p className="text-muted-foreground">Start new scraping jobs or view active task status.</p>
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
                    <div className="col-span-4">
                        <PlatformTaskForm onStartScrape={handleStartScrape} isLoading={isLoading} />
                    </div>

                    <div className="col-span-3">
                        {/* Reuse StatusCard from previous project structure */}
                        <StatusCard
                            status={status?.status || "idle"}
                            progress={status?.progress || []}
                            onDownload={handleDownload}
                        />
                    </div>
                </div>

                {/* Task History Table could go here (Step 9 in Prompt) */}
            </main>
        </div>
    );
}
