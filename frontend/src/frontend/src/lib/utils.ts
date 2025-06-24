// frontend/src/lib/utils.ts

/**
 * Tailwind CSS utility class merger
 * Example: cn("text-sm", isActive && "text-bold") => "text-sm text-bold"
 */
export function cn(...inputs: (string | false | null | undefined)[]): string {
  return inputs.filter(Boolean).join(" ");
}
