# TripIt Integration — MCP Server + Claude Skill

**Status**: Spec
**Date**: 2026-02-19
**Owner**: David O'Hara / Jarvis

---

## Goal

Pull David's travel data from TripIt automatically so Jarvis can generate pre-trip briefings, match flights to lounge recommendations, surface confirmation numbers, and keep the daily review travel-aware.

---

## Architecture

Two components:

1. **TripIt MCP Server** — A lightweight Node.js MCP server that authenticates with TripIt's API and exposes travel data as tools Jarvis can call natively in any conversation.
2. **Travel Brief Skill** — A Claude skill (`/travel-brief`) that combines TripIt data with the lounge guide, calendar, and prep checklists to generate a complete pre-trip package.

---

## Part 1: TripIt MCP Server

### Authentication

TripIt's v1 API supports two auth methods:

| Method | Use Case | Details |
|--------|----------|---------|
| **Basic HTTP Auth** | Development/testing only | `Authorization: Basic <base64(email:password)>`. Off by default — must email support@tripit.com to enable. |
| **OAuth 1.0a** | Production | 3-legged OAuth. Register app → get consumer key/secret → authorize once → store access token. Token persists indefinitely. |

**Recommendation**: OAuth 1.0a for production. Register an app at TripIt's developer portal. Authorize David's account once. Store tokens in a `.env` file or secure config.

### API Base URL

```
https://api.tripit.com/v1/
```

All responses default to XML. Append `/format/json` to any request for JSON.

### MCP Tools to Expose

#### `tripit_list_trips`
List upcoming (or past) trips.

```
GET /v1/list/trip/format/json
GET /v1/list/trip/past/true/format/json
GET /v1/list/trip/modified_since/{timestamp}/format/json
```

**Filters**:
- `past` (true/false) — default false (upcoming only)
- `traveler` (true/false/all) — default true
- `modified_since` (unix timestamp) — for incremental sync
- `include_objects` (true/false) — include all nested travel objects
- `page_num` / `page_size` — pagination (default: 5 trips per page)

**Returns**: Trip[] with id, display_name, start_date, end_date, primary_location, image_url, is_private

#### `tripit_get_trip`
Get a single trip with all associated objects.

```
GET /v1/get/trip/id/{trip_id}/include_objects/true/format/json
```

**Returns**: Full trip tree including:
- **AirObject[]** → AirSegment[] (flights with airline, flight #, airports, terminals, gates, seats, times, FlightStatus for Pro)
- **LodgingObject[]** (hotels with name, address, dates, confirmation #, room type)
- **CarObject[]** (rentals with company, type, pickup/dropoff locations, times)
- **ActivityObject[]** (events, conferences, meetings)
- **RestaurantObject[]** (dinner reservations)
- **RailObject[]**, **TransportObject[]**, **CruiseObject[]**
- **NoteObject[]** (attached notes/docs)
- **WeatherObject[]** (avg temps, precipitation — read-only, auto-populated)

#### `tripit_list_objects`
List travel objects with filters.

```
GET /v1/list/object/trip_id/{trip_id}/type/air/format/json
GET /v1/list/object/past/false/format/json
```

**Filters**:
- `trip_id` — objects within a specific trip
- `type` — filter by object type (air, lodging, car, activity, etc.)
- `past` (true/false)
- `traveler` (true/false/all)
- `modified_since` (timestamp)
- `page_num` / `page_size` (default: 25 objects per page)

#### `tripit_get_profile`
Get user profile and loyalty programs.

```
GET /v1/get/profile/format/json
```

**Returns**: Profile with screen_name, home_city, company, is_pro, email addresses, group memberships

#### `tripit_list_points_programs`
Get loyalty program balances (Pro only).

```
GET /v1/list/points_program/format/json
```

**Returns**: PointsProgram[] with name, account_number, balance, elite_status, elite_next_status, recent activity, upcoming expirations

#### `tripit_create_object` (optional — phase 2)
Create a travel object (note, activity, restaurant reservation, etc.).

```
POST /v1/create
Body: JSON object wrapped appropriately
```

### Key Object Schemas

#### AirSegment (the money fields for travel briefs)
```
start_airport_code      "DFW"
end_airport_code        "ATL"
start_city_name         "Dallas/Ft Worth, TX"
end_city_name           "Atlanta, GA"
start_terminal          "D"
start_gate              "D24"
end_terminal            "T"
end_gate                "T4"
marketing_airline       "American Airlines"
marketing_airline_code  "AA"
marketing_flight_number "1234"
operating_airline       (if codeshare)
aircraft                "Boeing 737-800"
service_class           "First"
seats                   "8A"
start_date_time         {date, time, timezone, utc_offset}
end_date_time           {date, time, timezone, utc_offset}
duration                "2h 30m"
distance                "721 miles"
baggage_claim           "B7"
check_in_url            "https://..."
```

#### FlightStatus (Pro only — real-time)
```
scheduled_departure     DateTime
estimated_departure     DateTime (delay detection)
scheduled_arrival       DateTime
estimated_arrival       DateTime
flight_status           int (enum: on-time, delayed, cancelled, etc.)
is_connection_at_risk   bool
departure_terminal      string (can differ from booked terminal)
departure_gate          string (real-time gate)
arrival_terminal        string
arrival_gate            string
baggage_claim           string
diverted_airport_code   string (if diverted)
last_modified           timestamp
```

#### LodgingObject (hotel fields)
```
supplier_name           "Hilton Garden Inn"
supplier_conf_num       "12345678"
record_locator          "ABC123"
address                 {addr1, city, state, zip, country, lat, lng}
room_type               "King Suite"
start_date_time         check-in
end_date_time           check-out
total_cost              "$450.00"
supplier_phone          "972-555-1234"
notes                   (any attached notes)
```

#### CarObject (rental fields)
```
supplier_name           "Sixt"
supplier_conf_num       "98765"
car_type                "Full Size Sedan"
start_location_name     "DFW Airport"
start_location_address  Address
end_location_name       "DFW Airport"
start_date_time         pickup
end_date_time           dropoff
mileage_charges         "Unlimited"
total_cost              "$189.00"
```

### MCP Server Implementation

```
tripit-mcp/
├── package.json
├── .env                 # TRIPIT_CONSUMER_KEY, TRIPIT_CONSUMER_SECRET,
│                        # TRIPIT_ACCESS_TOKEN, TRIPIT_ACCESS_TOKEN_SECRET
├── src/
│   ├── index.ts         # MCP server entry point
│   ├── auth.ts          # OAuth 1.0a signing
│   ├── client.ts        # TripIt API client (all endpoints)
│   ├── tools.ts         # MCP tool definitions
│   └── types.ts         # TypeScript interfaces for TripIt objects
└── README.md
```

**Dependencies**: `@modelcontextprotocol/sdk`, `oauth-1.0a`, `node-fetch`

### Setup Steps

1. Register a TripIt API application (get consumer key + secret)
2. Run OAuth authorization flow once (get access token + secret)
3. Store all 4 values in `.env`
4. Add MCP server to Claude config:
   ```json
   {
     "mcpServers": {
       "tripit": {
         "command": "node",
         "args": ["path/to/tripit-mcp/dist/index.js"],
         "env": {
           "TRIPIT_CONSUMER_KEY": "...",
           "TRIPIT_CONSUMER_SECRET": "...",
           "TRIPIT_ACCESS_TOKEN": "...",
           "TRIPIT_ACCESS_TOKEN_SECRET": "..."
         }
       }
     }
   }
   ```

---

## Part 2: Travel Brief Skill

### Trigger

`/travel-brief` or `/travel-brief {trip name}` or auto-triggered the night before any trip.

### What It Produces

A complete pre-trip briefing that combines TripIt data with David's preferences:

#### Flight Details
- Flight number, airline, departure/arrival times
- Terminal and gate (booked + real-time if Pro)
- Seat assignment
- Aircraft type
- Check-in URL
- Connection risk warnings

#### Lounge Recommendations
- Cross-reference departure airport + terminal with `reference/lounge-guide.md`
- Primary recommendation (Centurion > Admirals Club > Priority Pass)
- Walking time from gate to lounge
- Which card to show

#### Hotel Details
- Name, address, confirmation number
- Check-in/check-out times
- Loyalty program number (Hilton: 937667317, Marriott: 376585670, Hyatt: 538547033Y)
- Preferences reminder (higher floor, away from elevator)

#### Ground Transportation
- Rental car details + confirmation
- Or ride options if no rental

#### Weather
- Auto-populated by TripIt for destination
- Packing nudges if needed

#### Calendar Integration
- Pull meetings/events at destination from Outlook
- Flag any scheduling conflicts

#### Checklist
- [ ] Parking: DFW Terminal D pre-paid (dfwairport.com/park) or FreedomPark valet
- [ ] TSA PreCheck / Global Entry active
- [ ] Forward confirmations to plans@tripit.com
- [ ] Loyalty numbers loaded on reservations
- [ ] Check Amex/Citi card offers before purchasing anything at venue

### Skill File Structure

```
skills/travel-brief/
├── SKILL.md             # Skill instructions
├── templates/
│   └── brief.md         # Template for the travel brief output
└── README.md
```

### Data Flow

```
/travel-brief
    │
    ├── tripit_list_trips → find next upcoming trip
    ├── tripit_get_trip (include_objects=true) → full itinerary
    ├── Read reference/lounge-guide.md → lounge matching
    ├── outlook_calendar_search → meetings at destination
    ├── Read identity/MEMORY.md → preferences, loyalty numbers
    │
    └── Generate → Markdown travel brief
         └── Save to reviews/travel/ or bridge/outbox/
```

---

## Phase Plan

### Phase 1: MCP Server (core)
- [ ] Register TripIt API app
- [ ] Build OAuth flow + token storage
- [ ] Implement `tripit_list_trips` and `tripit_get_trip`
- [ ] Implement `tripit_list_objects`
- [ ] Test with David's account
- [ ] Add to Claude MCP config

### Phase 2: Travel Brief Skill
- [ ] Build skill template
- [ ] Integrate lounge guide cross-reference
- [ ] Integrate calendar lookup
- [ ] Integrate preferences from MEMORY.md
- [ ] Test with a real upcoming trip

### Phase 3: Automation
- [ ] Auto-trigger brief generation night before departure
- [ ] Real-time flight status checks day-of (requires Pro)
- [ ] Points program balance tracking
- [ ] Create objects from Jarvis (add restaurant reservations, notes, etc.)

---

## Decisions (2026-02-19)

1. **TripIt Pro** — Not now. Build for free API, but design FlightStatus and PointsProgram tools ready to activate on upgrade.
2. **Build Order** — Both MCP server and skill in parallel.
3. **Token Storage** — `.env` file, gitignored. Simple.
4. **Auto-Brief Timing** — Night before departure.
5. **API App Registration** — Added to OmniFocus inbox. David needs to register at TripIt's developer portal to get consumer key + secret.
