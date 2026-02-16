import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useRef } from "react";

interface StatusCardProps {
    status: string;
    progress: string[];
    onDownload: () => void;
}

export function StatusCard({ status, progress, onDownload }: StatusCardProps) {
    const logsRef = useRef<HTMLDivElement>(null);

    // Auto-scroll logs
    useEffect(() => {
        if (logsRef.current) {
            logsRef.current.scrollTop = logsRef.current.scrollHeight;
        }
    }, [progress]);

    return (
        <Card className="col-span-1 md:col-span-2 lg:col-span-3">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-base font-semibold">Live Logs</CardTitle>
                <div className="flex items-center gap-2">
                    <Badge variant={status === "completed" ? "default" : status === "failed" ? "destructive" : "secondary"}>
                        {status === "processing" && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
                        {status.toUpperCase()}
                    </Badge>
                    {status === "completed" && (
                        <Button size="sm" variant="outline" onClick={onDownload}>
                            <Download className="mr-2 h-4 w-4" />
                            CSV
                        </Button>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                <div ref={logsRef} className="h-[200px] w-full rounded-md border bg-muted/50 p-4 overflow-y-auto font-mono text-xs text-muted-foreground">
                    {progress.map((log, i) => (
                        <div key={i} className="mb-1 border-b border-border/40 pb-1 last:border-0 last:pb-0">
                            <span className="text-primary mr-2">[{new Date().toLocaleTimeString()}]</span>
                            {log}
                        </div>
                    ))}
                    {progress.length === 0 && <p className="italic">Waiting for task to start...</p>}
                </div>
            </CardContent>
        </Card>
    );
}
