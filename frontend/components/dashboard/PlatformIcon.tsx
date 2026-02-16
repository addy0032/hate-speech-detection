import { Youtube, Linkedin, Facebook, Instagram } from "lucide-react";
import { cn } from "@/lib/utils";

export type Platform = "linkedin" | "youtube" | "instagram" | "facebook";

interface PlatformIconProps {
    platform: Platform;
    className?: string;
}

export function PlatformIcon({ platform, className }: PlatformIconProps) {
    switch (platform) {
        case "linkedin":
            return <Linkedin className={cn("text-blue-600", className)} />;
        case "youtube":
            return <Youtube className={cn("text-red-600", className)} />;
        case "facebook":
            return <Facebook className={cn("text-blue-500", className)} />;
        case "instagram":
            return <Instagram className={cn("text-pink-600", className)} />; // Gradient would be better but keeping simple for icon
        default:
            return null;
    }
}

export function getPlatformColor(platform: Platform) {
    switch (platform) {
        case "linkedin": return "bg-blue-50 border-blue-200 text-blue-700";
        case "youtube": return "bg-red-50 border-red-200 text-red-700";
        case "facebook": return "bg-blue-50 border-blue-200 text-blue-600";
        case "instagram": return "bg-pink-50 border-pink-200 text-pink-700";
        default: return "bg-slate-50 border-slate-200";
    }
}
