import React from 'react';
import CustomCard from '@/components/ui/custom-card';
import { Badge } from '@/components/ui/badge';
import { Loader, MessageSquare, ShieldCheck, TrendingUp, TrendingDown, Scale } from '@/utils/icons';
import { Separator } from '@/components/ui/separator';

interface AgentAnalysisResult {
    symbol: string;
    analyst_reports: {
        technical: string;
        fundamental: string;
        sentiment: string;
    };
    research_cases: {
        bullish: string;
        bearish: string;
    };
    final_decision: string;
}

interface AgentAnalysisPanelProps {
    data: AgentAnalysisResult | null;
    isLoading: boolean;
    onRunAnalysis: () => void;
}

const AgentAnalysisPanel: React.FC<AgentAnalysisPanelProps> = ({ data, isLoading, onRunAnalysis }) => {
    if (isLoading) {
        return (
            <div className="py-20 flex flex-col items-center justify-center space-y-4">
                <Loader className="h-10 w-10 animate-spin text-primary" />
                <div className="text-center">
                    <p className="font-bold text-lg animate-pulse">Consulting Multi-Agent Team...</p>
                    <p className="text-sm text-muted-foreground mt-1">Analysts are gathering data & Researchers are debating cases.</p>
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="py-12 flex flex-col items-center justify-center text-center border-2 border-dashed rounded-xl">
                <Scale className="h-12 w-12 text-muted-foreground/30 mb-4" />
                <h3 className="text-lg font-bold">Deep Agent Consensus</h3>
                <p className="text-sm text-muted-foreground max-w-md mt-2 mb-6">
                    Trigger a collaborative session between specialized AI agents to get a high-conviction trade recommendation.
                </p>
                <button
                    onClick={onRunAnalysis}
                    className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-bold hover:opacity-90 transition-opacity"
                >
                    Run Multi-Agent Analysis
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Final Decision Hero */}
            <div className="p-6 bg-primary/5 border border-primary/20 rounded-2xl relative overflow-hidden">
                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">Final Consensus</Badge>
                        <Badge variant="secondary" className="bg-amber-500/10 text-amber-600 border-amber-200">Local Llama 3.1</Badge>
                    </div>
                    <div className="whitespace-pre-wrap font-serif text-lg leading-relaxed italic text-foreground/90">
                        {data.final_decision}
                    </div>
                </div>
                <ShieldCheck className="absolute -bottom-4 -right-4 h-32 w-32 text-primary/5 -rotate-12" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Peer Debate Section */}
                <div className="space-y-4">
                    <h4 className="font-bold flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 text-primary" />
                        The Researcher Debate
                    </h4>

                    <div className="p-4 bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/30 rounded-xl relative">
                        <div className="flex items-center gap-2 mb-2 text-emerald-700 dark:text-emerald-400 font-bold text-xs uppercase tracking-wider">
                            <TrendingUp className="h-3 w-3" />
                            Bull Case (Optimist)
                        </div>
                        <div className="text-sm text-muted-foreground line-clamp-[10] whitespace-pre-wrap">
                            {data.research_cases.bullish}
                        </div>
                    </div>

                    <div className="p-4 bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/30 rounded-xl">
                        <div className="flex items-center gap-2 mb-2 text-rose-700 dark:text-rose-400 font-bold text-xs uppercase tracking-wider">
                            <TrendingDown className="h-3 w-3" />
                            Bear Case (Skeptic)
                        </div>
                        <div className="text-sm text-muted-foreground line-clamp-[10] whitespace-pre-wrap">
                            {data.research_cases.bearish}
                        </div>
                    </div>
                </div>

                {/* Analyst Reports Section */}
                <div className="space-y-4">
                    <h4 className="font-bold flex items-center gap-2">
                        <Scale className="h-4 w-4 text-primary" />
                        Analyst Inputs
                    </h4>

                    <div className="space-y-3">
                        {['Technical', 'Fundamental', 'Sentiment'].map((role) => (
                            <div key={role} className="border rounded-lg overflow-hidden">
                                <div className="bg-muted px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest flex justify-between items-center">
                                    {role} Analysis
                                    <Badge variant="outline" className="text-[8px] h-4 py-0">Completed</Badge>
                                </div>
                                <div className="p-3 text-xs text-muted-foreground whitespace-pre-wrap max-h-32 overflow-y-auto italic">
                                    {(data.analyst_reports as any)[role.toLowerCase()]}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <Separator />

            <div className="flex justify-center pb-4">
                <button
                    onClick={onRunAnalysis}
                    className="text-xs text-muted-foreground hover:text-primary transition-colors flex items-center gap-2"
                >
                    <Loader className="h-3 w-3" />
                    Refresh Analysis (Force Agent Re-evaluation)
                </button>
            </div>
        </div>
    );
};

export default AgentAnalysisPanel;
