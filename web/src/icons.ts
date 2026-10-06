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
  swords: svg(`<path d="M4 4l10 10M4 4v3.5M4 4h3.5M11 17l3-3M12.5 18.5l-3-3M16 16l4 4"/><path d="M20 4 10 14M20 4v3.5M20 4h-3.5M13 17l-3-3M11.5 18.5l3-3M8 16l-4 4"/>`),
  medal: svg(`<circle cx="12" cy="14.5" r="5.5"/><path d="M8.5 9.5 6 3h4l2 4.5L14 3h4l-2.5 6.5"/>`),
  flag: svg(`<path d="M5 21V4"/><path d="M5 4.5h12l-2.5 4 2.5 4H5"/>`),
  star: svg(`<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8z"/>`),
  flame: svg(`<path d="M12 21c3.3 0 6-2.5 6-6 0-4-3-5.5-4-10-2.5 1.5-3.5 3.5-3.5 5.5-1-.5-1.5-1.5-1.5-2.5C7.5 9.5 6 12 6 15c0 3.5 2.7 6 6 6Z"/>`),
  key: svg(`<circle cx="8" cy="15" r="4"/><path d="M11 12l8.5-8.5M16 6.5l2.5 2.5M13.5 9l2 2"/>`),
  bolt: svg(`<path d="M13 3 5 13.5h6L10 21l8-10.5h-6z"/>`),
  up: svg(`<path d="M12 20V5"/><path d="M5.5 11.5 12 5l6.5 6.5"/>`),
  misc: svg(`<circle cx="7" cy="7" r="3"/><rect x="14" y="4" width="6" height="6"/><path d="M7 14l3.5 6h-7z"/><path d="M14 14l6 6M20 14l-6 6"/>`),
};
