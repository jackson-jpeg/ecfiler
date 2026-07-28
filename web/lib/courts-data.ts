// Client-side court directory and event-code data.
//
// The JSON files under lib/data/ are exact copies of the Python source of
// truth in ecfiler/courts/data/ — tests/test_web_data_parity.py fails the
// build if they drift. The search logic mirrors ecfiler/courts/registry.py
// and ecfiler/filing/events.py so the static site behaves like the API did.

import districtCourts from "./data/district_courts.json";
import bankruptcyCourts from "./data/bankruptcy_courts.json";
import appellateCourts from "./data/appellate_courts.json";
import districtEvents from "./data/event_codes/common_district.json";
import bankruptcyEvents from "./data/event_codes/common_bankruptcy.json";
import appellateEvents from "./data/event_codes/common_appellate.json";

export interface Court {
  court_id: string;
  name: string;
  court_type: string;
}

export interface EventCode {
  code: string;
  description: string;
  category: string;
}

interface RawCourt {
  court_id: string;
  name: string;
  court_type: string;
}

interface RawEventFile {
  court_type: string;
  categories: Record<string, { code: string; description: string }[]>;
}

const ALL_COURTS: Court[] = (
  [...districtCourts, ...bankruptcyCourts, ...appellateCourts] as RawCourt[]
).map((c) => ({ court_id: c.court_id, name: c.name, court_type: c.court_type }));

const COURT_TYPE_BY_ID = new Map(ALL_COURTS.map((c) => [c.court_id, c.court_type]));

const EVENTS_BY_TYPE: Record<string, EventCode[]> = Object.fromEntries(
  (
    [
      ["district", districtEvents],
      ["bankruptcy", bankruptcyEvents],
      ["appellate", appellateEvents],
    ] as [string, RawEventFile][]
  ).map(([type, file]) => [
    type,
    Object.entries(file.categories).flatMap(([category, codes]) =>
      codes.map((e) => ({ code: e.code, description: e.description, category }))
    ),
  ])
);

export function listCourts(courtType?: string): Court[] {
  const courts = ALL_COURTS.filter((c) => !courtType || c.court_type === courtType);
  return [...courts].sort((a, b) => a.court_id.localeCompare(b.court_id));
}

export function searchCourts(query?: string, courtType?: string): Court[] {
  if (!query) return listCourts(courtType);
  const queryLower = query.toLowerCase().trim();
  const words = queryLower.split(/\s+/);
  const results = ALL_COURTS.filter((c) => {
    if (courtType && c.court_type !== courtType) return false;
    const searchable = `${c.court_id} ${c.name}`.toLowerCase();
    return words.every((w) => searchable.includes(w));
  });
  results.sort((a, b) => {
    const aExact = a.court_id.toLowerCase() === queryLower ? 0 : 1;
    const bExact = b.court_id.toLowerCase() === queryLower ? 0 : 1;
    return aExact - bExact || a.name.localeCompare(b.name);
  });
  return results;
}

export function getEvents(courtId: string, search?: string): EventCode[] {
  const courtType = COURT_TYPE_BY_ID.get(courtId) ?? "district";
  const events = EVENTS_BY_TYPE[courtType] ?? EVENTS_BY_TYPE.district;
  if (!search) return events;

  // Bidirectional relevance scoring, mirroring events.search_events:
  // exact > description-inside-query (prefix bonus) > query-inside-description
  // > word overlap of two or more words.
  const queryLower = search.toLowerCase();
  const queryWords = new Set(queryLower.split(/\s+/));
  const scored: [number, EventCode][] = [];
  for (const e of events) {
    const descLower = e.description.toLowerCase();
    const descWords = descLower.split(/\s+/);
    if (queryLower === descLower) {
      scored.push([1000, e]);
    } else if (queryLower.includes(descLower)) {
      const bonus = queryLower.startsWith(descLower) ? 50 : 0;
      scored.push([100 + descLower.length + bonus, e]);
    } else if (descLower.includes(queryLower)) {
      scored.push([90, e]);
    } else {
      const overlap = descWords.filter((w) => queryWords.has(w)).length;
      if (overlap >= 2) {
        const pct = descWords.length ? overlap / descWords.length : 0;
        scored.push([overlap * 10 + pct * 5, e]);
      }
    }
  }
  scored.sort((a, b) => b[0] - a[0]);
  return scored.map(([, e]) => e);
}

export const TOTAL_COURT_COUNT = ALL_COURTS.length;
