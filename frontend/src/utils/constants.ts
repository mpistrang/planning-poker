export const CARD_VALUES = [
  "0",
  "0.5",
  "1",
  "2",
  "3",
  "5",
  "8",
  "13",
  "?",
  "☕",
] as const;

export type CardValue = (typeof CARD_VALUES)[number];

export const WS_URL = import.meta.env.VITE_WS_URL || "http://localhost:8000";
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
