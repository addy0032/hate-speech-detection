import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, MessageSquare } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { CommentItem } from "./CommentItem";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface PostCardProps {
    postUrl: string;
    comments: any[];
    index: number;
}

export function PostCard({ postUrl, comments, index }: PostCardProps) {
    const [expanded, setExpanded] = useState(false);
    const displayComments = expanded ? comments : comments.slice(0, 2);

    return (
        <Card className="flex flex-col h-full hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-3">
                <div className="grid gap-1">
                    <CardTitle className="text-base font-semibold flex items-center gap-2">
                        Post #{index}
                        <a href={postUrl} target="_blank" rel="noreferrer" className="text-muted-foreground hover:text-primary">
                            <ExternalLink className="h-4 w-4" />
                        </a>
                    </CardTitle>
                </div>
                <Badge variant="secondary" className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    {comments.length}
                </Badge>
            </CardHeader>
            <CardContent className="grid gap-4 flex-1">
                <div className="text-xs text-muted-foreground truncate" title={postUrl}>
                    {postUrl}
                </div>
                <div className="grid gap-2">
                    {displayComments.map((c: any, i: number) => (
                        <CommentItem
                            key={i}
                            author={c.author_name || "Unknown"}
                            text={c.comment}
                            label={c.label}
                            profileUrl={c.user_profile_url}
                        />
                    ))}
                </div>
                {comments.length > 2 && (
                    <Button
                        variant="ghost"
                        size="sm"
                        className="w-full mt-auto"
                        onClick={() => setExpanded(!expanded)}
                    >
                        {expanded ? "Show Less" : `View all ${comments.length} comments`}
                    </Button>
                )}
            </CardContent>
        </Card>
    );
}
