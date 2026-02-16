import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, AlertTriangle, ShieldCheck, FileText, Activity } from "lucide-react";

interface StatsProps {
    totalPosts: number;
    totalComments: number;
    hateCount: number;
    activePlatforms?: number;
}

export function StatsCards({ totalPosts, totalComments, hateCount, activePlatforms = 1 }: StatsProps) {
    const safeCount = totalComments - hateCount;

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Content Scraped</CardTitle>
                    <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{totalPosts}</div>
                    <p className="text-xs text-muted-foreground">
                        Posts & Videos processed
                    </p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Comments Analyzed</CardTitle>
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{totalComments}</div>
                    <p className="text-xs text-muted-foreground">
                        Across {activePlatforms} active platforms
                    </p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Hate Speech Detected</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-destructive" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold text-destructive">{hateCount}</div>
                    <p className="text-xs text-muted-foreground">
                        Comments flagged as toxic/hate
                    </p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Safe Comments</CardTitle>
                    <ShieldCheck className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold text-green-600">{safeCount}</div>
                    <p className="text-xs text-muted-foreground">
                        Cleared analysis
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
