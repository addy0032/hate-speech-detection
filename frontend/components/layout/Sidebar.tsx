'use client';

import { BarChart3, Database, FileText, Settings, ShieldCheck, Github, LayoutDashboard, ListTodo } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { PlatformIcon, Platform } from "@/components/dashboard/PlatformIcon";
import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> { }

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname();
    const [platformsOpen, setPlatformsOpen] = useState(true);

    const isActive = (path: string) => pathname === path;

    return (
        <div className={cn("pb-12 min-h-screen border-r bg-card", className)}>
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <div className="mb-6 px-4 text-lg font-semibold tracking-tight text-primary flex items-center gap-2">
                        <ShieldCheck className="h-6 w-6 text-indigo-600" />
                        <span>SocialGuard</span>
                    </div>

                    <div className="space-y-1">
                        <Link href="/dashboard">
                            <Button variant={isActive("/dashboard") ? "secondary" : "ghost"} className="w-full justify-start">
                                <LayoutDashboard className="mr-2 h-4 w-4" />
                                Overview
                            </Button>
                        </Link>
                        <Link href="/tasks">
                            <Button variant={isActive("/tasks") ? "secondary" : "ghost"} className="w-full justify-start">
                                <ListTodo className="mr-2 h-4 w-4" />
                                Scraping Tasks
                            </Button>
                        </Link>
                        <Link href="/reports">
                            <Button variant={isActive("/reports") ? "secondary" : "ghost"} className="w-full justify-start">
                                <FileText className="mr-2 h-4 w-4" />
                                Reports
                            </Button>
                        </Link>
                        <Link href="/analytics">
                            <Button variant={isActive("/analytics") ? "secondary" : "ghost"} className="w-full justify-start">
                                <BarChart3 className="mr-2 h-4 w-4" />
                                Analytics
                            </Button>
                        </Link>
                        <Link href="/settings">
                            <Button variant={isActive("/settings") ? "secondary" : "ghost"} className="w-full justify-start">
                                <Settings className="mr-2 h-4 w-4" />
                                Settings
                            </Button>
                        </Link>
                    </div>
                </div>

                <div className="px-3 py-2">
                    <button
                        onClick={() => setPlatformsOpen(!platformsOpen)}
                        className="flex items-center justify-between w-full mb-2 px-4 text-xs font-semibold uppercase tracking-tight text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <span>Platforms</span>
                        {platformsOpen ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                    </button>

                    {platformsOpen && (
                        <div className="space-y-1">
                            <Link href="/results?platform=linkedin">
                                <Button variant="ghost" className="w-full justify-start pl-4 font-normal">
                                    <PlatformIcon platform="linkedin" className="mr-2 h-4 w-4" />
                                    LinkedIn
                                    <span className="ml-auto text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">Active</span>
                                </Button>
                            </Link>
                            <Link href="/results?platform=youtube">
                                <Button variant="ghost" className="w-full justify-start pl-4 font-normal">
                                    <PlatformIcon platform="youtube" className="mr-2 h-4 w-4" />
                                    YouTube
                                    <span className="ml-auto text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">Active</span>
                                </Button>
                            </Link>
                            <Link href="/results?platform=instagram">
                                <Button variant="ghost" className="w-full justify-start pl-4 font-normal">
                                    <PlatformIcon platform="instagram" className="mr-2 h-4 w-4" />
                                    Instagram
                                    <span className="ml-auto text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">Active</span>
                                </Button>
                            </Link>
                            <Button variant="ghost" className="w-full justify-start pl-4 font-normal opacity-60" disabled>
                                <PlatformIcon platform="facebook" className="mr-2 h-4 w-4" />
                                Facebook
                                <span className="ml-auto text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded-full">Soon</span>
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
