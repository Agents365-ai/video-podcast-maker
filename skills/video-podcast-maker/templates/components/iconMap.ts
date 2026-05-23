import * as LucideIcons from "lucide-react";
import type { LucideIcon } from "lucide-react";

/**
 * Convert kebab-case or lowercase icon names to PascalCase for Lucide lookup.
 * Examples: "arrow-right" → "ArrowRight", "rocket" → "Rocket", "cpu" → "Cpu"
 */
function toPascalCase(name: string): string {
  return name
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
}

/**
 * Look up any Lucide icon by name (kebab-case, lowercase, or PascalCase).
 * Returns undefined if not found.
 */
export function getLucideIcon(name: string): LucideIcon | undefined {
  const pascalName = toPascalCase(name);
  const icon = (LucideIcons as Record<string, unknown>)[pascalName];
  if (typeof icon === "function") {
    return icon as LucideIcon;
  }
  return undefined;
}

export const isEmoji = (s: string): boolean => {
  if (s.length > 4) return false;
  return /\p{Emoji}/u.test(s);
};
