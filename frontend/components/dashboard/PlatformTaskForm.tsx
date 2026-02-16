'use client';

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Loader2, Play } from "lucide-react";
import { PlatformIcon, Platform } from "./PlatformIcon";

interface PlatformTaskFormProps {
    onStartScrape: (platform: Platform, urls: string[], days: number) => Promise<void>;
    isLoading: boolean;
}

export function PlatformTaskForm({ onStartScrape, isLoading }: PlatformTaskFormProps) {
    const [platform, setPlatform] = useState<Platform>("linkedin");
    const [urls, setUrls] = useState("");
    const [days, setDays] = useState(30);

    const handleSubmit = () => {
        if (!urls.trim()) return;
        const urlList = urls.split("\n").map(u => u.trim()).filter(u => u.length > 0);
        onStartScrape(platform, urlList, days);
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Create New Scraping Task</CardTitle>
                <CardDescription>
                    Select a platform and configure your scraping parameters.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="linkedin" onValueChange={(v: string) => setPlatform(v as Platform)} className="w-full">
                    <TabsList className="grid w-full grid-cols-2 mb-6">
                        <TabsTrigger value="linkedin" className="flex items-center gap-2">
                            <PlatformIcon platform="linkedin" className="h-4 w-4" />
                            LinkedIn
                        </TabsTrigger>
                        <TabsTrigger value="youtube" className="flex items-center gap-2">
                            <PlatformIcon platform="youtube" className="h-4 w-4" />
                            YouTube
                        </TabsTrigger>
                    </TabsList>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="urls">
                                {platform === "linkedin" ? "Target URLs (Posts or Pages)" : "Channel URL or Username"}
                            </Label>
                            <Textarea
                                id="urls"
                                value={urls}
                                onChange={(e) => setUrls(e.target.value)}
                                placeholder={platform === "linkedin"
                                    ? "https://www.linkedin.com/company/...\nhttps://www.linkedin.com/posts/..."
                                    : "https://www.youtube.com/@ChannelName"
                                }
                                className="font-mono text-sm min-h-[120px]"
                                disabled={isLoading}
                            />
                            <p className="text-[0.8rem] text-muted-foreground">
                                {platform === "linkedin"
                                    ? "One URL per line."
                                    : "Enter the full channel URL or username."
                                }
                            </p>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="days">Lookback Period (Days)</Label>
                            <Input
                                id="days"
                                type="number"
                                value={days}
                                onChange={(e) => setDays(Number(e.target.value))}
                                min={1}
                                className="max-w-[150px]"
                                disabled={isLoading}
                            />
                        </div>

                        <div className="flex justify-end pt-4">
                            <Button
                                onClick={handleSubmit}
                                disabled={isLoading || !urls.trim()}
                                className={platform === "linkedin" ? "bg-blue-600 hover:bg-blue-700" : "bg-red-600 hover:bg-red-700"}
                                size="lg"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Starting...
                                    </>
                                ) : (
                                    <>
                                        <Play className="mr-2 h-4 w-4 fill-current" />
                                        Start {platform === "linkedin" ? "LinkedIn" : "YouTube"} Scrape
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                </Tabs>
            </CardContent>
        </Card>
    );
}
