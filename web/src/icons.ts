const svg = (body: string, size = 20, stroke = 1.6) =>
  `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;

export const icons = {
  mark: svg(`<path d="M5 8l5 4-5 4"/><path d="M12 17h7"/>`, 18, 2.2),
  home: svg(`<rect x="3.5" y="3.5" width="7" height="7"/><rect x="13.5" y="3.5" width="7" height="7"/><rect x="3.5" y="13.5" width="7" height="7"/><path d="M13.5 17h7M17 13.5v7"/>`),
  terminal: svg(`<rect x="3" y="4.5" width="18" height="15"/><path d="M7 10l3 2.5L7 15"/><path d="M12.5 15H17"/>`),
  search: svg(`<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/>`, 16, 1.7),
  sun: svg(`<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>`),
  moon: svg(`<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/>`),
  play: svg(`<path d="M7 5l12 7-12 7z"/>`, 13, 2),
  check: svg(`<path d="M4 12.5l5 5L20 6.5"/>`, 13, 2.2),
  reset: svg(`<path d="M4 4v6h6"/><path d="M5.5 15a7.5 7.5 0 1 0 1.8-7.8L4 10"/>`, 13, 2),
  bulb: svg(`<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/>`, 14, 1.8),
  book: svg(`<path d="M4 4.5h6a2.5 2.5 0 0 1 2.5 2.5v12A2 2 0 0 0 10.5 17H4z"/><path d="M20 4.5h-6A2.5 2.5 0 0 0 11.5 7v12A2 2 0 0 1 13.5 17H20z"/>`),
  code: svg(`<path d="M8.5 8.5 4 12l4.5 3.5"/><path d="M15.5 8.5 20 12l-4.5 3.5"/><path d="M13.5 5l-3 14"/>`),
  left: svg(`<path d="M15 5l-7 7 7 7"/>`, 14, 2),
  right: svg(`<path d="M9 5l7 7-7 7"/>`, 14, 2),
};
