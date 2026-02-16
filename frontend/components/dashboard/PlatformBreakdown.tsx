import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { PlatformIcon, Platform, getPlatformColor } from "./PlatformIcon";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface PlatformStats {
    platform: Platform;
    postsScraped: number;
    commentsAnalyzed: number;
    hateCount: number;
    lastScrape?: string;
    isActive: boolean;
}

interface PlatformBreakdownProps {
    stats: PlatformStats[];
}

export function PlatformBreakdown({ stats }: PlatformBreakdownProps) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
                <Link href={stat.isActive ? `/results?platform=${stat.platform}` : '#'} key={stat.platform} className={!stat.isActive ? "pointer-events-none opacity-60" : ""}>
                    <Card className={cn("hover:shadow-md transition-all cursor-pointer border-t-4", getPlatformColor(stat.platform).split(' ')[1].replace('text-', 'border-t-'))}>
                        <CardHeader className="pb-2">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <PlatformIcon platform={stat.platform} className="h-5 w-5" />
                                    <CardTitle className="text-base">{stat.platform.charAt(0).toUpperCase() + stat.platform.slice(1)}</CardTitle>
                                </div>
                                {stat.isActive ? (
                                    <div className="bg-green-100 text-green-700 text-[10px] px-2 py-0.5 rounded-full font-medium">Active</div>
                                ) : (
                                    <div className="bg-slate-100 text-slate-500 text-[10px] px-2 py-0.5 rounded-full font-medium">Coming Soon</div>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-1 mt-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Content Scraped</span>
                                    <span className="font-medium">{stat.postsScraped}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Comments</span>
                                    <span className="font-medium">{stat.commentsAnalyzed}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Hate Speech</span>
                                    <span className="font-medium text-destructive">{stat.hateCount}</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </Link>
            ))}
        </div>
    );
}
