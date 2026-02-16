import { Bell, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"; // Need to check if dropdown-menu exists, if not use simple button for now
import { Badge } from "@/components/ui/badge";

export function Navbar() {
    return (
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6 shadow-sm">
            <div className="flex flex-1 items-center gap-2">
                <h1 className="text-lg font-semibold md:text-xl">Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
                <Button variant="outline" size="icon" className="relative">
                    <Bell className="h-4 w-4" />
                    <span className="absolute -top-1 -right-1 flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-sky-500"></span>
                    </span>
                </Button>
                <Button variant="ghost" size="icon" className="rounded-full bg-muted">
                    <User className="h-5 w-5" />
                </Button>
            </div>
        </header>
    );
}
