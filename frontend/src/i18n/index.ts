import { en } from './en';
import { th } from './th';

export const translations = { th, en } as const;
export type Language = keyof typeof translations;
export type TranslationKey = keyof typeof th;
export type Translation = Record<TranslationKey, string>;
export const DEFAULT_LANGUAGE: Language = 'th';
