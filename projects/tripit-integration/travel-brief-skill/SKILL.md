# Travel Brief Skill

## Trigger

`/travel-brief` — generates a pre-trip briefing for the next upcoming trip.
`/travel-brief {trip name}` — generates a briefing for a specific trip.

## Prerequisites

- TripIt MCP server running and connected
- `reference/lounge-guide.md` exists
- `identity/MEMORY.md` accessible for preferences

## Workflow

1. **Fetch trip data**: Call `tripit_list_trips` to get upcoming trips. If no trip name specified, use the next chronological trip. If trip name specified, fuzzy match against display_name.

2. **Fetch full itinerary**: Call `tripit_get_trip` with `include_objects=true` to get all travel objects.

3. **Process flight segments**: For each AirSegment, extract:
   - Flight number (marketing_airline_code + marketing_flight_number)
   - Departure/arrival airports, terminals, gates
   - Times (local to each airport)
   - Seat assignment
   - Aircraft type
   - Check-in URL
   - If Pro: FlightStatus (delays, real-time gate, connection risk)

4. **Match lounges**: Read `reference/lounge-guide.md`. For each departure airport:
   - Find the airport in the guide
   - Match the terminal from the AirSegment
   - Apply preference order: Centurion > Admirals Club > Priority Pass
   - Include which card to present
   - Note any terminal-change requirements

5. **Process hotel**: For each LodgingObject, extract:
   - Hotel name, address, phone
   - Confirmation number (supplier_conf_num or record_locator)
   - Check-in/check-out dates and times
   - Room type
   - Match hotel chain to loyalty number from MEMORY.md:
     - Hilton → 937667317
     - Marriott → 376585670
     - Hyatt → 538547033Y
   - Reminder: higher floor, away from elevator

6. **Process ground transport**: For each CarObject:
   - Rental company, car type
   - Pickup/dropoff locations and times
   - Confirmation number
   - Match rental company to loyalty number from MEMORY.md:
     - Sixt → 16022388
     - Hertz → 54437875
     - Avis → 4XX10E

7. **Check calendar**: Call `outlook_calendar_search` for meetings during the trip dates at the destination city. Flag conflicts with flight times.

8. **Check weather**: Pull WeatherObject from trip data. Convert Celsius to Fahrenheit. Add packing nudges if extreme temps or rain expected.

9. **Generate brief**: Use the template below. Save to `reviews/travel/{trip-start-date}-{destination}.md`.

## Output Template

```markdown
# Travel Brief: {trip_display_name}
**{start_date} — {end_date}** | {primary_location}
Generated: {current_date}

---

## Flights

### {departure_date} — {start_city} → {end_city}
- **{airline_code} {flight_number}** | {aircraft}
- Departs: {start_time} from {start_airport} Terminal {terminal}, Gate {gate}
- Arrives: {end_time} at {end_airport} Terminal {terminal}
- Seat: {seat} | Class: {service_class}
- Confirmation: {record_locator}
- [Check in]({check_in_url})

**Lounge**: {lounge_recommendation} — show {card_name}
{terminal_change_note_if_needed}

---

## Hotel

**{hotel_name}**
{address}
Check-in: {checkin_date} | Check-out: {checkout_date}
Confirmation: {conf_num}
Loyalty #: {loyalty_number}
Phone: {phone}
Room: {room_type}
📋 Request higher floor, away from elevator

---

## Rental Car

**{supplier_name}** — {car_type}
Pickup: {start_location} at {start_time}
Dropoff: {end_location} at {end_time}
Confirmation: {conf_num}
Loyalty #: {loyalty_number}

---

## Weather at {destination}

{weather_summary}
{packing_note_if_applicable}

---

## Meetings at Destination

{calendar_events_list}

---

## Pre-Trip Checklist

- [ ] Parking: DFW Terminal D pre-paid (dfwairport.com/park) or FreedomPark valet
- [ ] Check in for flight(s)
- [ ] Loyalty numbers loaded on reservations
- [ ] Check Amex/Citi card-linked offers for destination
- [ ] Confirmations forwarded to plans@tripit.com
```

## Error Handling

- If TripIt MCP not connected: inform user and suggest running the server
- If no upcoming trips: "No upcoming trips in TripIt. Forward a confirmation to plans@tripit.com to get started."
- If trip name doesn't match: show list of upcoming trips and ask which one
- If lounge guide missing for an airport: note "No lounge data for {airport} — update reference/lounge-guide.md"
