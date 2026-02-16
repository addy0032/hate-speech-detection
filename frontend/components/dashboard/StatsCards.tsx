import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, AlertTriangle, ShieldCheck, FileText } from "lucide-react";

interface StatsProps {
    totalPosts: number;
    totalComments: number;
    hateCount: number;
    toxicCount: number;
}

export function StatsCards({ totalPosts, totalComments, hateCount, toxicCount }: StatsProps) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Posts Scraped</CardTitle>
                    <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{totalPosts}</div>
                    <p className="text-xs text-muted-foreground">
                        +100% since last run
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
                        Parsed from {totalPosts} posts
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
                        Requires immediate attention
                    </p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Safe Comments</CardTitle>
                    <ShieldCheck className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold text-green-500">
                        {totalComments - (hateCount + toxicCount)}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Flagged as safe content
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
