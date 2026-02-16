import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface CommentProps {
    author: string;
    text: string;
    label: string;
    profileUrl?: string; // Add profileUrl prop
}

export function CommentItem({ author, text, label, profileUrl }: CommentProps) {
    const getBadgeColor = (lbl: string) => {
        switch (lbl.toLowerCase()) {
            case "hate": return "destructive"; // Red
            case "toxic": return "destructive"; // Red/Orange if custom variant exists
            case "sarcasm": return "secondary"; // Gray/Blue
            case "safe": return "outline"; // Green-ish via class override or safe
            default: return "outline";
        }
    };

    const isSafe = label.toLowerCase() === "safe";

    return (
        <div className="flex items-start gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors border border-transparent hover:border-border/50">
            <Avatar className="h-8 w-8">
                <AvatarImage src={profileUrl} alt={author} /> {/* Use actual image if available in future */}
                <AvatarFallback>{author.substring(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div className="grid gap-1.5 flex-1">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm">{author}</span>
                        {profileUrl && (
                            <a href={profileUrl} target="_blank" rel="noreferrer" className="text-xs text-muted-foreground hover:underline">
                                (Profile)
                            </a>
                        )}
                    </div>
                    <Badge variant={getBadgeColor(label)} className={isSafe ? "text-green-600 border-green-200 bg-green-50" : ""}>
                        {label}
                    </Badge>
                </div>
                <p className="text-sm text-muted-foreground break-words line-clamp-3 hover:line-clamp-none transition-all">
                    {text}
                </p>
            </div>
        </div>
    );
}
