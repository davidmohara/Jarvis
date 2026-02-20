// TripIt API v1 — TypeScript interfaces
// Derived from tripit-api-obj-v1.xsd via Go binding

// --- Primitives ---

export interface DateTime {
  date: string;
  time: string;
  timezone: string;
  utc_offset: string;
}

export interface Address {
  address: string;
  addr1: string;
  addr2: string;
  city: string;
  state: string;
  zip: string;
  country: string;
  latitude: number;
  longitude: number;
}

export interface Image {
  caption: string;
  url: string;
}

export interface Traveler {
  first_name: string;
  middle_name: string;
  last_name: string;
  frequent_traveler_num: string;
  frequent_traveler_supplier: string;
  meal_preference: string;
  seat_preference: string;
  ticket_num: string;
}

// --- Flight Status (Pro only) ---

export interface FlightStatus {
  scheduled_departure_date_time: DateTime;
  estimated_departure_date_time: DateTime;
  scheduled_arrival_date_time: DateTime;
  estimated_arrival_date_time: DateTime;
  flight_status: number;
  is_connection_at_risk: boolean;
  departure_terminal: string;
  departure_gate: string;
  arrival_terminal: string;
  arrival_gate: string;
  layover_minutes: string;
  baggage_claim: string;
  diverted_airport_code: string;
  last_modified: string;
}

// --- Trip ---

export interface Trip {
  id: string;
  relative_url: string;
  start_date: string;
  end_date: string;
  description: string;
  display_name: string;
  image_url: string;
  is_private: boolean;
  primary_location: string;
  primary_location_address: Address;
}

// --- Reservation Base (shared by Air, Lodging, Car, etc.) ---

interface ReservationBase {
  id: string;
  trip_id: string;
  is_client_traveler: boolean;
  relative_url: string;
  display_name: string;
  image: Image[];
  cancellation_date_time: DateTime;
  booking_date: string;
  booking_rate: string;
  booking_site_conf_num: string;
  booking_site_name: string;
  booking_site_phone: string;
  booking_site_url: string;
  record_locator: string;
  supplier_conf_num: string;
  supplier_contact: string;
  supplier_email_address: string;
  supplier_name: string;
  supplier_phone: string;
  supplier_url: string;
  is_purchased: boolean;
  notes: string;
  restrictions: string;
  total_cost: string;
}

// --- Air ---

export interface AirSegment {
  id: string;
  status: FlightStatus;
  start_date_time: DateTime;
  end_date_time: DateTime;
  start_airport_code: string;
  start_airport_latitude: number;
  start_airport_longitude: number;
  start_city_name: string;
  start_gate: string;
  start_terminal: string;
  end_airport_code: string;
  end_airport_latitude: number;
  end_airport_longitude: number;
  end_city_name: string;
  end_gate: string;
  end_terminal: string;
  marketing_airline: string;
  marketing_airline_code: string;
  marketing_flight_number: string;
  operating_airline: string;
  operating_airline_code: string;
  operating_flight_number: string;
  alternative_flights_url: string;
  aircraft: string;
  aircraft_display_name: string;
  distance: string;
  duration: string;
  entertainment: string;
  meal: string;
  notes: string;
  ontime_perc: string;
  seats: string;
  service_class: string;
  stops: string;
  baggage_claim: string;
  check_in_url: string;
  is_hidden: boolean;
}

export interface AirObject extends ReservationBase {
  Segment: AirSegment[];
  Traveler: Traveler[];
}

// --- Lodging ---

export interface LodgingObject extends ReservationBase {
  start_date_time: DateTime;
  end_date_time: DateTime;
  address: Address;
  Guest: Traveler[];
  number_guests: string;
  number_rooms: string;
  room_type: string;
}

// --- Car ---

export interface CarObject extends ReservationBase {
  start_date_time: DateTime;
  end_date_time: DateTime;
  start_location_address: Address;
  end_location_address: Address;
  Driver: Traveler[];
  start_location_hours: string;
  start_location_name: string;
  start_location_phone: string;
  end_location_hours: string;
  end_location_name: string;
  end_location_phone: string;
  car_description: string;
  car_type: string;
  mileage_charges: string;
}

// --- Activity ---

export interface ActivityObject extends ReservationBase {
  start_date_time: DateTime;
  end_time: string;
  address: Address;
  Participant: Traveler[];
  detail_type_code: string;
  location_name: string;
}

// --- Restaurant ---

export interface RestaurantObject extends ReservationBase {
  date_time: DateTime;
  address: Address;
  ReservationHolder: Traveler;
  cuisine: string;
  dress_code: string;
  hours: string;
  number_patrons: string;
  price_range: string;
}

// --- Rail ---

export interface RailSegment {
  id: string;
  start_date_time: DateTime;
  end_date_time: DateTime;
  start_station_address: Address;
  end_station_address: Address;
  start_station_name: string;
  end_station_name: string;
  carrier_name: string;
  coach_number: string;
  confirmation_num: string;
  seats: string;
  service_class: string;
  train_number: string;
  train_type: string;
}

export interface RailObject extends ReservationBase {
  Segment: RailSegment[];
  Traveler: Traveler[];
}

// --- Transport ---

export interface TransportSegment {
  id: string;
  start_date_time: DateTime;
  end_date_time: DateTime;
  start_location_address: Address;
  end_location_address: Address;
  start_location_name: string;
  end_location_name: string;
  detail_type_code: string;
  carrier_name: string;
  confirmation_num: string;
  number_passengers: string;
  vehicle_description: string;
}

export interface TransportObject extends ReservationBase {
  Segment: TransportSegment[];
  Traveler: Traveler[];
}

// --- Cruise ---

export interface CruiseSegment {
  id: string;
  start_date_time: DateTime;
  end_date_time: DateTime;
  location_address: Address;
  location_name: string;
  detail_type_code: string;
}

export interface CruiseObject extends ReservationBase {
  Segment: CruiseSegment[];
  Traveler: Traveler[];
  cabin_number: string;
  cabin_type: string;
  dining: string;
  ship_name: string;
}

// --- Note, Map, Directions ---

export interface NoteObject {
  id: string;
  trip_id: string;
  display_name: string;
  date_time: DateTime;
  address: Address;
  detail_type_code: string;
  source: string;
  text: string;
  url: string;
  notes: string;
}

export interface MapObject {
  id: string;
  trip_id: string;
  display_name: string;
  date_time: DateTime;
  address: Address;
}

export interface DirectionsObject {
  id: string;
  trip_id: string;
  display_name: string;
  date_time: DateTime;
  start_address: Address;
  end_address: Address;
}

// --- Weather (read-only) ---

export interface WeatherObject {
  id: string;
  trip_id: string;
  display_name: string;
  date: string;
  location: string;
  avg_high_temp_c: number;
  avg_low_temp_c: number;
  avg_wind_speed_kn: number;
  avg_precipitation_cm: number;
  avg_snow_depth_cm: number;
}

// --- Points Programs (Pro only) ---

export interface PointsProgramActivity {
  date: string;
  description: string;
  base: string;
  bonus: string;
  total: string;
}

export interface PointsProgramExpiration {
  date: string;
  amount: string;
}

export interface PointsProgram {
  id: number;
  name: string;
  account_number: string;
  account_login: string;
  balance: string;
  elite_status: string;
  elite_next_status: string;
  elite_ytd_qualify: string;
  elite_need_to_earn: string;
  last_modified: string;
  Activity: PointsProgramActivity[];
  Expiration: PointsProgramExpiration[];
}

// --- Profile ---

export interface Profile {
  is_client: boolean;
  is_pro: boolean;
  screen_name: string;
  public_display_name: string;
  profile_url: string;
  home_city: string;
  company: string;
  photo_url: string;
}

// --- API Response ---

export interface TripItResponse {
  timestamp: string;
  num_bytes: number;
  page_num?: number;
  page_size?: number;
  max_page?: number;
  Trip?: Trip | Trip[];
  AirObject?: AirObject | AirObject[];
  LodgingObject?: LodgingObject | LodgingObject[];
  CarObject?: CarObject | CarObject[];
  ActivityObject?: ActivityObject | ActivityObject[];
  RestaurantObject?: RestaurantObject | RestaurantObject[];
  RailObject?: RailObject | RailObject[];
  TransportObject?: TransportObject | TransportObject[];
  CruiseObject?: CruiseObject | CruiseObject[];
  NoteObject?: NoteObject | NoteObject[];
  MapObject?: MapObject | MapObject[];
  DirectionsObject?: DirectionsObject | DirectionsObject[];
  WeatherObject?: WeatherObject | WeatherObject[];
  PointsProgram?: PointsProgram | PointsProgram[];
  Profile?: Profile | Profile[];
}
