import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { PlatformIcon, Platform } from "./PlatformIcon";
import { formatDistanceToNow } from "date-fns";
import { MessageSquare, AlertTriangle, CheckCircle, ExternalLink } from "lucide-react";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";

interface ContentCardProps {
    platform: Platform;
    title?: string;
    url: string;
    thumbnail?: string;
    timestamp?: string; // ISO string
    commentCount: number;
    hateCount: number;
    safeCount?: number;
    author?: string;
}

export function ContentCard({
    platform,
    title,
    url,
    thumbnail,
    timestamp,
    commentCount,
    hateCount,
    safeCount,
    author
}: ContentCardProps) {

    const dateStr = timestamp ? formatDistanceToNow(new Date(timestamp), { addSuffix: true }) : "Unknown date";

    return (
        <Card className={`overflow-hidden border-l-4 hover:shadow-md transition-shadow ${platform === 'linkedin' ? 'border-l-blue-500' :
                platform === 'youtube' ? 'border-l-red-500' : 'border-l-gray-500'
            }`}>
            <CardHeader className="p-4 pb-2 space-y-0">
                <div className="flex justify-between items-start gap-2">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <PlatformIcon platform={platform} className="h-4 w-4" />
                        <span>{platform === 'linkedin' ? 'Post' : 'Video'}</span>
                        <span>•</span>
                        <span>{dateStr}</span>
                    </div>
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                        <ExternalLink className="h-4 w-4" />
                    </a>
                </div>
                <h3 className="font-semibold leading-tight text-base line-clamp-2">
                    {title || url}
                </h3>
                {author && <p className="text-sm text-muted-foreground">{author}</p>}
            </CardHeader>

            <CardContent className="p-4 pt-2">
                {thumbnail && (
                    <div className="relative w-full h-32 mb-3 rounded-md overflow-hidden bg-slate-100">
                        {/* Use normal img tag if Image optimization is tricky with external URLs without config */}
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
                    </div>
                )}

                <div className="flex gap-2 text-sm">
                    {/* Snippet or other info */}
                </div>
            </CardContent>

            <CardFooter className="p-4 pt-0 flex justify-between items-center text-sm border-t bg-slate-50/50 mt-auto">
                <div className="flex gap-4">
                    <div className="flex items-center gap-1.5" title="Total Comments">
                        <MessageSquare className="h-4 w-4 text-slate-500" />
                        <span className="font-medium">{commentCount}</span>
                    </div>
                    <div className="flex items-center gap-1.5" title="Hate/Info">
                        {hateCount > 0 ? (
                            <Badge variant="destructive" className="h-5 px-1.5 rounded-sm">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                {hateCount}
                            </Badge>
                        ) : (
                            <Badge variant="outline" className="h-5 px-1.5 rounded-sm border-green-200 text-green-700 bg-green-50">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Clean
                            </Badge>
                        )}
                    </div>
                </div>
            </CardFooter>
        </Card>
    );
}
