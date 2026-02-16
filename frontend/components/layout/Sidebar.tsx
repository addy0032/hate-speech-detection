import { BarChart3, Database, FileText, Settings, ShieldCheck, Github } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils"; // Assuming you have a utils file or create one
import { Button } from "@/components/ui/button";

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> { }

export function Sidebar({ className }: SidebarProps) {
    return (
        <div className={cn("pb-12 min-h-screen border-r bg-card", className)}>
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <div className="mb-2 px-4 text-lg font-semibold tracking-tight text-primary flex items-center gap-2">
                        <ShieldCheck className="h-6 w-6" />
                        <span>HateSpeech.AI</span>
                    </div>
                    <div className="space-y-1">
                        <Button variant="secondary" className="w-full justify-start">
                            <Database className="mr-2 h-4 w-4" />
                            Scraper Dashboard
                        </Button>
                        <Button variant="ghost" className="w-full justify-start">
                            <FileText className="mr-2 h-4 w-4" />
                            Reports
                        </Button>
                        <Button variant="ghost" className="w-full justify-start">
                            <BarChart3 className="mr-2 h-4 w-4" />
                            Analytics
                        </Button>
                        <Button variant="ghost" className="w-full justify-start">
                            <Settings className="mr-2 h-4 w-4" />
                            Settings
                        </Button>
                    </div>
                </div>
                <div className="px-3 py-2">
                    <h2 className="mb-2 px-4 text-xs font-semibold uppercase tracking-tight text-muted-foreground">
                        Project Links
                    </h2>
                    <div className="space-y-1">
                        <a href="https://github.com" target="_blank" rel="noreferrer">
                            <Button variant="ghost" className="w-full justify-start">
                                <Github className="mr-2 h-4 w-4" />
                                GitHub Repo
                            </Button>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}
