
import React from 'react';
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { Loader, Info } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface FormGroupProps {
  htmlFor: string;
  label: string;
  error?: string;
  optional?: boolean;
  className?: string;
  children: React.ReactNode;
  tooltip?: string;
  isLoading?: boolean;
  hint?: string;
}

const FormGroup = ({
  htmlFor,
  label,
  error,
  optional = false,
  className,
  children,
  tooltip,
  isLoading = false,
  hint,
}: FormGroupProps) => {
  return (
    <div className={cn("mb-4", className)}>
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-1">
          <Label htmlFor={htmlFor} className="text-sm font-medium">
            {label}
          </Label>
          {isLoading && <Loader className="h-3 w-3 animate-spin text-muted-foreground" />}
          {tooltip && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-3 w-3 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{tooltip}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
        {optional && (
          <span className="text-xs text-muted-foreground">Optional</span>
        )}
      </div>
      {children}
      {hint && !error && (
        <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
      )}
      {error && (
        <p className="mt-1.5 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
};

export default FormGroup;
