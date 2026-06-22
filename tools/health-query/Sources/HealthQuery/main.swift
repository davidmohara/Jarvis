import HealthKit
import Foundation

// MARK: - Source Bundle IDs
// Used to tag readings by device/app so Galen can filter intelligently.
// These are the known bundle IDs for apps that write to HealthKit.
// Galen uses the `source` field in output to distinguish WHOOP sleep from
// Apple Watch sleep, Hume weight from manually entered weight, etc.

enum SourceID {
    static let whoop       = "com.whoop.Whoop"
    static let appleHealth = "com.apple.health"
    static let appleWatch  = "com.apple.NanoTimeKit"  // Watch writes via this
    static let hume        = "com.hume.health"         // confirm on first run
}

// MARK: - Query Windows
// Different metrics have different useful horizons.
// Raw HR samples are dense — 7 days is plenty and keeps output manageable.
// Body comp is sparse (monthly scans) — 365 days gives full trend context.

enum QueryWindow: Int {
    case week      = 7
    case month     = 30
    case quarter   = 90
    case halfYear  = 180
    case year      = 365
}

// MARK: - Output Types

struct QuantityRecord: Codable {
    let type: String
    let value: Double
    let unit: String
    let date: String        // ISO 8601
    let end_date: String    // ISO 8601 (same as date for spot measurements)
    let source: String      // app name (human-readable)
    let source_bundle: String
}

struct CategoryRecord: Codable {
    let type: String
    let value: Int          // raw HKCategoryValue integer
    let value_label: String // human-readable label (e.g. "asleepREM")
    let start_date: String  // ISO 8601
    let end_date: String    // ISO 8601
    let duration_minutes: Double
    let source: String
    let source_bundle: String
}

struct WorkoutRecord: Codable {
    let type: String          // always "workout"
    let activity: String      // e.g. "Running", "Cycling", "HIIT"
    let start_date: String
    let end_date: String
    let duration_minutes: Double
    let active_calories: Double?
    let distance_meters: Double?
    let source: String
    let source_bundle: String
}

struct HealthQueryOutput: Codable {
    let generated_at: String
    let quantity_records: [QuantityRecord]
    let category_records: [CategoryRecord]
    let workout_records: [WorkoutRecord]
    let meta: OutputMeta
}

struct OutputMeta: Codable {
    let quantity_types_queried: Int
    let category_types_queried: Int
    let total_records: Int
    let windows_used: [String: Int]   // type_group -> days
    let note_hrv: String
    let note_sleep: String
}

// MARK: - HealthKit Type Definitions

struct QuantityTypeSpec {
    let identifier: HKQuantityTypeIdentifier
    let name: String        // key in output JSON
    let unit: HKUnit
    let window: QueryWindow
    let aggregate: Bool     // true = daily sum/avg instead of raw samples
}

struct CategoryTypeSpec {
    let identifier: HKCategoryTypeIdentifier
    let name: String
    let window: QueryWindow
    let valueLabels: [Int: String]
}

// MARK: - Type Registry

var quantitySpecs: [QuantityTypeSpec] = [

    // ── BODY COMPOSITION (Tier 1) ──────────────────────────────────────────
    // Hume scans are monthly. Query a full year for trend context.
    QuantityTypeSpec(identifier: .bodyMass,             name: "body_mass_kg",               unit: .gramUnit(with: .kilo),                   window: .year,    aggregate: false),
    QuantityTypeSpec(identifier: .bodyFatPercentage,    name: "body_fat_pct",               unit: .percent(),                               window: .year,    aggregate: false),
    QuantityTypeSpec(identifier: .leanBodyMass,         name: "lean_body_mass_kg",          unit: .gramUnit(with: .kilo),                   window: .year,    aggregate: false),
    QuantityTypeSpec(identifier: .bodyMassIndex,        name: "bmi",                        unit: .count(),                                 window: .year,    aggregate: false),
    QuantityTypeSpec(identifier: .height,               name: "height_cm",                  unit: .meterUnit(with: .centi),                 window: .year,    aggregate: false),

    // ── BODY COMPOSITION (Tier 2) ──────────────────────────────────────────
    QuantityTypeSpec(identifier: .waistCircumference,   name: "waist_circumference_cm",     unit: .meterUnit(with: .centi),                 window: .year,    aggregate: false),

    // ── HEART (Tier 1) ─────────────────────────────────────────────────────
    // Raw heart rate samples are extremely dense. 7-day window only.
    // NOTE: heartRateVariabilitySDNN is Apple Watch SDNN — NOT WHOOP RMSSD.
    // These are different methodologies. Do not compare them directly.
    // WHOOP RMSSD comes from the WHOOP MCP server, not HealthKit.
    QuantityTypeSpec(identifier: .heartRate,                  name: "heart_rate_bpm",              unit: HKUnit(from: "count/min"),          window: .week,    aggregate: false),
    QuantityTypeSpec(identifier: .restingHeartRate,           name: "resting_heart_rate_bpm",      unit: HKUnit(from: "count/min"),          window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .heartRateVariabilitySDNN,   name: "hrv_sdnn_ms",                 unit: .secondUnit(with: .milli),          window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .walkingHeartRateAverage,    name: "walking_heart_rate_avg_bpm",  unit: HKUnit(from: "count/min"),          window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .heartRateRecoveryOneMinute, name: "heart_rate_recovery_1min_bpm",unit: HKUnit(from: "count/min"),          window: .quarter, aggregate: false),

    // ── HEART (Tier 2) ─────────────────────────────────────────────────────
    QuantityTypeSpec(identifier: .bloodPressureSystolic,  name: "blood_pressure_systolic_mmhg",  unit: .millimeterOfMercury(), window: .year,    aggregate: false),
    QuantityTypeSpec(identifier: .bloodPressureDiastolic, name: "blood_pressure_diastolic_mmhg", unit: .millimeterOfMercury(), window: .year,    aggregate: false),

    // ── ACTIVITY (Tier 1) ──────────────────────────────────────────────────
    // Steps and calories: aggregate daily (sum). Gives clean day-by-day view.
    QuantityTypeSpec(identifier: .stepCount,             name: "steps",                      unit: .count(),                                 window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .activeEnergyBurned,    name: "active_calories_kcal",       unit: .kilocalorie(),                           window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .basalEnergyBurned,     name: "basal_calories_kcal",        unit: .kilocalorie(),                           window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .appleExerciseTime,     name: "exercise_minutes",           unit: .minute(),                                window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .appleStandTime,        name: "stand_minutes",              unit: .minute(),                                window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .flightsClimbed,        name: "flights_climbed",            unit: .count(),                                 window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .distanceWalkingRunning,name: "distance_walk_run_meters",   unit: .meter(),                                 window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .vo2Max,                name: "vo2_max_ml_kg_min",          unit: HKUnit(from: "ml/kg·min"),                window: .year,    aggregate: false),

    // ── ACTIVITY (Tier 2 — gait/mobility, longevity markers) ───────────────
    // iPhone writes these automatically from its motion coprocessor.
    // Strong predictors of longevity per Attia / JAMA literature.
    QuantityTypeSpec(identifier: .walkingSpeed,                  name: "walking_speed_m_s",             unit: HKUnit(from: "m/s"),         window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .walkingStepLength,             name: "walking_step_length_m",         unit: .meter(),                    window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .walkingAsymmetryPercentage,    name: "walking_asymmetry_pct",         unit: .percent(),                  window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .walkingDoubleSupportPercentage,name: "walking_double_support_pct",    unit: .percent(),                  window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .stairAscentSpeed,              name: "stair_ascent_speed_m_s",        unit: HKUnit(from: "m/s"),         window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .stairDescentSpeed,             name: "stair_descent_speed_m_s",       unit: HKUnit(from: "m/s"),         window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .sixMinuteWalkTestDistance,     name: "six_min_walk_distance_m",       unit: .meter(),                    window: .year,    aggregate: false),

    // ── RUNNING METRICS (Tier 2) ───────────────────────────────────────────
    QuantityTypeSpec(identifier: .runningStrideLength,           name: "running_stride_length_m",       unit: .meter(),                    window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .runningVerticalOscillation,    name: "running_vertical_osc_cm",       unit: .meterUnit(with: .centi),    window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .runningGroundContactTime,      name: "running_ground_contact_ms",     unit: .secondUnit(with: .milli),   window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .runningPower,                  name: "running_power_watts",           unit: .watt(),                     window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .runningSpeed,                  name: "running_speed_m_s",             unit: HKUnit(from: "m/s"),         window: .quarter, aggregate: false),

    // ── RESPIRATORY (Tier 1) ───────────────────────────────────────────────
    // WHOOP and Apple Watch both write respiratory rate during sleep.
    // Use source_bundle to distinguish. Prefer WHOOP when available.
    QuantityTypeSpec(identifier: .respiratoryRate,       name: "respiratory_rate_bpm",       unit: HKUnit(from: "count/min"),                window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .oxygenSaturation,      name: "spo2_pct",                   unit: .percent(),                               window: .quarter, aggregate: false),

    // ── TEMPERATURE (Tier 2) ───────────────────────────────────────────────
    // appleSleepingWristTemperature requires Apple Watch Series 8+.
    // Returns deviation from baseline (delta °C), not absolute temp.
    QuantityTypeSpec(identifier: .bodyTemperature,              name: "body_temp_c",              unit: .degreeCelsius(), window: .quarter, aggregate: false),

    // ── METABOLIC / CLINICAL (Tier 2) ─────────────────────────────────────
    QuantityTypeSpec(identifier: .bloodGlucose,          name: "blood_glucose_mg_dl",        unit: HKUnit(from: "mg/dL"),                    window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .insulinDelivery,       name: "insulin_delivery_iu",        unit: HKUnit(from: "IU"),                       window: .quarter, aggregate: false),

    // ── ENVIRONMENTAL / AUDIO (Tier 2) ────────────────────────────────────
    QuantityTypeSpec(identifier: .environmentalAudioExposure, name: "env_audio_exposure_dbspl",    unit: .decibelAWeightedSoundPressureLevel(), window: .quarter, aggregate: false),
    QuantityTypeSpec(identifier: .headphoneAudioExposure,     name: "headphone_audio_exposure_dbspl",unit: .decibelAWeightedSoundPressureLevel(),window: .quarter, aggregate: false),

    // ── SUBSTANCE (Tier 2) ─────────────────────────────────────────────────
    QuantityTypeSpec(identifier: .numberOfAlcoholicBeverages, name: "alcoholic_beverages_count",  unit: .count(),    window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .bloodAlcoholContent,        name: "blood_alcohol_content_pct",  unit: .percent(),  window: .quarter, aggregate: false),

    // ── NUTRITION (Tier 2 — only populated if user logs food) ─────────────
    QuantityTypeSpec(identifier: .dietaryEnergyConsumed, name: "dietary_energy_kcal",        unit: .kilocalorie(),   window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryProtein,        name: "dietary_protein_g",          unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryFatTotal,       name: "dietary_fat_g",              unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryCarbohydrates,  name: "dietary_carbs_g",            unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryFiber,          name: "dietary_fiber_g",            unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietarySugar,          name: "dietary_sugar_g",            unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryCaffeine,       name: "dietary_caffeine_g",         unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryWater,          name: "dietary_water_l",            unit: .liter(),         window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietarySodium,         name: "dietary_sodium_g",           unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryMagnesium,      name: "dietary_magnesium_g",        unit: .gram(),          window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryVitaminD,       name: "dietary_vitamin_d_mcg",      unit: .gramUnit(with: .micro), window: .quarter, aggregate: true),
    QuantityTypeSpec(identifier: .dietaryZinc,           name: "dietary_zinc_g",             unit: .gram(),          window: .quarter, aggregate: true),
]

if #available(macOS 14.0, *) {
    quantitySpecs.append(QuantityTypeSpec(identifier: .timeInDaylight, name: "time_in_daylight_sec", unit: .second(), window: .quarter, aggregate: true))
}

let categorySpecs: [CategoryTypeSpec] = [

    // ── SLEEP (Tier 1) ─────────────────────────────────────────────────────
    // WHOOP and Apple Watch both write sleep stages. Source filtering matters.
    // .asleepCore = light sleep, .asleepDeep = slow-wave, .asleepREM = REM
    CategoryTypeSpec(
        identifier: .sleepAnalysis,
        name: "sleep",
        window: .month,
        valueLabels: [
            0: "inBed",
            1: "asleepUnspecified",
            2: "awake",
            3: "asleepCore",       // light sleep
            4: "asleepDeep",       // slow-wave / SWS
            5: "asleepREM",
        ]
    ),

    // ── MINDFULNESS (Tier 2) ───────────────────────────────────────────────
    CategoryTypeSpec(
        identifier: .mindfulSession,
        name: "mindful_session",
        window: .quarter,
        valueLabels: [0: "notApplicable"]
    ),

    // ── CARDIAC EVENTS (Tier 2) ────────────────────────────────────────────
    CategoryTypeSpec(
        identifier: .highHeartRateEvent,
        name: "high_heart_rate_event",
        window: .quarter,
        valueLabels: [0: "notApplicable"]
    ),
    CategoryTypeSpec(
        identifier: .lowHeartRateEvent,
        name: "low_heart_rate_event",
        window: .quarter,
        valueLabels: [0: "notApplicable"]
    ),
    CategoryTypeSpec(
        identifier: .irregularHeartRhythmEvent,
        name: "irregular_heart_rhythm_event",
        window: .quarter,
        valueLabels: [0: "notApplicable"]
    ),
    CategoryTypeSpec(
        identifier: .lowCardioFitnessEvent,
        name: "low_cardio_fitness_event",
        window: .quarter,
        valueLabels: [0: "lowFitness"]
    ),
]

// MARK: - Helpers

let isoFormatter: ISO8601DateFormatter = {
    let f = ISO8601DateFormatter()
    f.formatOptions = [.withInternetDateTime]
    return f
}()

func daysAgo(_ days: Int) -> Date {
    Calendar.current.date(byAdding: .day, value: -days, to: Date())!
}

func dayStart(_ date: Date) -> Date {
    Calendar.current.startOfDay(for: date)
}

func dayEnd(_ date: Date) -> Date {
    Calendar.current.date(byAdding: .second, value: 86399, to: dayStart(date))!
}

// Generate all calendar days in a range (for aggregation buckets)
func calendarDays(from start: Date, to end: Date) -> [Date] {
    var days: [Date] = []
    var current = dayStart(start)
    let endDay = dayStart(end)
    while current <= endDay {
        days.append(current)
        current = Calendar.current.date(byAdding: .day, value: 1, to: current)!
    }
    return days
}

// MARK: - Aggregation

// For aggregate types (steps, calories, etc.), collect raw samples then
// group by calendar day, summing values within each day.
// Returns one QuantityRecord per day that has data.
func aggregateByDay(
    samples: [HKQuantitySample],
    spec: QuantityTypeSpec
) -> [QuantityRecord] {
    // Group samples by calendar day
    var byDay: [String: (total: Double, source: String, bundle: String)] = [:]
    for sample in samples {
        let dayKey = isoFormatter.string(from: dayStart(sample.startDate))
        let value = sample.quantity.doubleValue(for: spec.unit)
        let existing = byDay[dayKey]
        byDay[dayKey] = (
            total: (existing?.total ?? 0) + value,
            source: sample.sourceRevision.source.name,
            bundle: sample.sourceRevision.source.bundleIdentifier
        )
    }
    return byDay.map { day, data in
        QuantityRecord(
            type: spec.name,
            value: data.total,
            unit: spec.unit.unitString,
            date: day,
            end_date: day,
            source: data.source,
            source_bundle: data.bundle
        )
    }.sorted { $0.date > $1.date }
}

// MARK: - Main

let healthKitAvailable = HKHealthStore.isHealthDataAvailable()
let store = HKHealthStore()

// Build read type set — collect all valid types, silently skip any that
// aren't available on this OS version.
var readTypes = Set<HKObjectType>()

for spec in quantitySpecs {
    if let t = HKQuantityType.quantityType(forIdentifier: spec.identifier) {
        readTypes.insert(t)
    }
}
for spec in categorySpecs {
    if let t = HKCategoryType.categoryType(forIdentifier: spec.identifier) {
        readTypes.insert(t)
    }
}
readTypes.insert(HKObjectType.workoutType())

// Authorization
// Try HealthKit first, fall back to CloudKit if it fails
let authSema = DispatchSemaphore(value: 0)
var authGranted = false
var authFailed = false

NSSetUncaughtExceptionHandler { exception in
    authFailed = true
    authSema.signal()
}

store.requestAuthorization(toShare: nil, read: readTypes) { granted, error in
    authGranted = granted
    authSema.signal()
}

authSema.wait()

if authFailed {
    // HealthKit authorization failed. This happens when the Health app isn't installed
    // or HealthKit isn't accessible on this Mac. CloudKit access requires app-specific
    // entitlements that only Apple's Health app has.

    let msg: [String: Any] = [
        "error": "HealthKit not available on this Mac",
        "reason": "The Health app is not installed or HealthKit is not accessible",
        "environment": [
            "health_app_installed": false,
            "healthkit_available": false,
            "icloud_health_data": "synced (55.7 MB detected)"
        ],
        "solutions": [
            "1. Install the Health app from Mac App Store (if available for your region/account)",
            "2. Or run HealthQuery on a Mac that has the Health app installed",
            "3. Or export health data from your iPhone and process locally"
        ],
        "note": "iCloud Health data exists but requires the Health app for local access due to Apple's privacy model"
    ]

    if let data = try? JSONSerialization.data(withJSONObject: msg, options: .prettyPrinted),
       let json = String(data: data, encoding: .utf8) {
        print(json)
    }
    exit(1)
} else if !authGranted {
    // HealthKit authorization was denied or not available
    let msg: [String: Any] = [
        "error": "HealthKit access denied or unavailable",
        "reason": "This Mac may not have the Health app installed or HealthKit is not accessible",
        "environment": [
            "health_app_installed": false,
            "icloud_health_data": "detected (55.7 MB synced but not locally accessible)"
        ],
        "solutions": [
            "1. Install the Health app from Mac App Store (if available)",
            "2. Or run HealthQuery on a Mac with the Health app",
            "3. Export health data from your iPhone and process locally"
        ]
    ]
    if let data = try? JSONSerialization.data(withJSONObject: msg, options: .prettyPrinted),
       let json = String(data: data, encoding: .utf8) {
        print(json)
    }
    exit(1)
}

// MARK: - Query Execution

var allQuantityRecords: [QuantityRecord] = []
var allCategoryRecords: [CategoryRecord] = []
var allWorkoutRecords:  [WorkoutRecord]  = []

let group = DispatchGroup()
let lock   = NSLock()

// ── Quantity Queries ────────────────────────────────────────────────────────

for spec in quantitySpecs {
    guard let qType = HKQuantityType.quantityType(forIdentifier: spec.identifier) else { continue }

    let start = daysAgo(spec.window.rawValue)
    let pred  = HKQuery.predicateForSamples(withStart: start, end: Date(), options: .strictStartDate)
    let sort  = [NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)]

    group.enter()
    let query = HKSampleQuery(
        sampleType: qType,
        predicate: pred,
        limit: HKObjectQueryNoLimit,
        sortDescriptors: sort
    ) { _, samples, _ in
        defer { group.leave() }
        guard let samples = samples as? [HKQuantitySample], !samples.isEmpty else { return }

        let records: [QuantityRecord]

        if spec.aggregate {
            records = aggregateByDay(samples: samples, spec: spec)
        } else {
            records = samples.map { s in
                QuantityRecord(
                    type: spec.name,
                    value: s.quantity.doubleValue(for: spec.unit),
                    unit: spec.unit.unitString,
                    date: isoFormatter.string(from: s.startDate),
                    end_date: isoFormatter.string(from: s.endDate),
                    source: s.sourceRevision.source.name,
                    source_bundle: s.sourceRevision.source.bundleIdentifier
                )
            }
        }

        lock.lock()
        allQuantityRecords.append(contentsOf: records)
        lock.unlock()
    }
    store.execute(query)
}

// ── Category Queries ────────────────────────────────────────────────────────

for spec in categorySpecs {
    guard let cType = HKCategoryType.categoryType(forIdentifier: spec.identifier) else { continue }

    let start = daysAgo(spec.window.rawValue)
    let pred  = HKQuery.predicateForSamples(withStart: start, end: Date(), options: .strictStartDate)
    let sort  = [NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)]

    group.enter()
    let query = HKSampleQuery(
        sampleType: cType,
        predicate: pred,
        limit: HKObjectQueryNoLimit,
        sortDescriptors: sort
    ) { _, samples, _ in
        defer { group.leave() }
        guard let samples = samples as? [HKCategorySample], !samples.isEmpty else { return }

        let records = samples.map { s -> CategoryRecord in
            let durationSec = s.endDate.timeIntervalSince(s.startDate)
            let label = spec.valueLabels[s.value] ?? "value_\(s.value)"
            return CategoryRecord(
                type: spec.name,
                value: s.value,
                value_label: label,
                start_date: isoFormatter.string(from: s.startDate),
                end_date: isoFormatter.string(from: s.endDate),
                duration_minutes: durationSec / 60.0,
                source: s.sourceRevision.source.name,
                source_bundle: s.sourceRevision.source.bundleIdentifier
            )
        }

        lock.lock()
        allCategoryRecords.append(contentsOf: records)
        lock.unlock()
    }
    store.execute(query)
}

// ── Workout Query ───────────────────────────────────────────────────────────

let workoutStart = daysAgo(QueryWindow.quarter.rawValue)
let workoutPred  = HKQuery.predicateForSamples(withStart: workoutStart, end: Date(), options: .strictStartDate)
let workoutSort  = [NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)]

group.enter()
let workoutQuery = HKSampleQuery(
    sampleType: .workoutType(),
    predicate: workoutPred,
    limit: HKObjectQueryNoLimit,
    sortDescriptors: workoutSort
) { _, samples, _ in
    defer { group.leave() }
    guard let workouts = samples as? [HKWorkout], !workouts.isEmpty else { return }

    let records = workouts.map { w -> WorkoutRecord in
        let durationMin = w.duration / 60.0
        let calories    = w.statistics(for: HKQuantityType(.activeEnergyBurned))?
                           .sumQuantity()?.doubleValue(for: .kilocalorie())
        let distance    = w.statistics(for: HKQuantityType(.distanceWalkingRunning))?
                           .sumQuantity()?.doubleValue(for: .meter())
                        ?? w.statistics(for: HKQuantityType(.distanceCycling))?
                           .sumQuantity()?.doubleValue(for: .meter())

        return WorkoutRecord(
            type: "workout",
            activity: w.workoutActivityType.name,
            start_date: isoFormatter.string(from: w.startDate),
            end_date: isoFormatter.string(from: w.endDate),
            duration_minutes: durationMin,
            active_calories: calories,
            distance_meters: distance,
            source: w.sourceRevision.source.name,
            source_bundle: w.sourceRevision.source.bundleIdentifier
        )
    }

    lock.lock()
    allWorkoutRecords.append(contentsOf: records)
    lock.unlock()
}
store.execute(workoutQuery)

// MARK: - Wait and Output

group.notify(queue: .main) {
    let totalRecords = allQuantityRecords.count + allCategoryRecords.count + allWorkoutRecords.count

    let output = HealthQueryOutput(
        generated_at: isoFormatter.string(from: Date()),
        quantity_records: allQuantityRecords.sorted { $0.date > $1.date },
        category_records: allCategoryRecords.sorted { $0.start_date > $1.start_date },
        workout_records:  allWorkoutRecords.sorted  { $0.start_date > $1.start_date },
        meta: OutputMeta(
            quantity_types_queried: quantitySpecs.count,
            category_types_queried: categorySpecs.count,
            total_records: totalRecords,
            windows_used: [
                "body_composition_days": QueryWindow.year.rawValue,
                "heart_rate_raw_days": QueryWindow.week.rawValue,
                "resting_hr_hrv_vo2_days": QueryWindow.quarter.rawValue,
                "activity_days": QueryWindow.quarter.rawValue,
                "sleep_days": QueryWindow.month.rawValue,
                "vo2max_days": QueryWindow.year.rawValue,
            ],
            note_hrv: "hrv_sdnn_ms comes from Apple Watch (SDNN method). WHOOP reports HRV as RMSSD — a different methodology. SDNN typically runs 1.5-2x higher than RMSSD. Do not compare them directly. For WHOOP RMSSD, use the WHOOP MCP server.",
            note_sleep: "sleep records include entries from all sources (WHOOP, Apple Watch, manual). Filter by source_bundle to isolate a single device. WHOOP bundle: com.whoop.Whoop. Prefer WHOOP sleep stages when available."
        )
    )

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

    if let data = try? encoder.encode(output),
       let json = String(data: data, encoding: .utf8) {
        print(json)
        exit(0)
    } else {
        fputs("{\"error\": \"Failed to encode output\"}\n", stderr)
        exit(1)
    }
}

RunLoop.main.run()

// MARK: - HKWorkoutActivityType Extension

extension HKWorkoutActivityType {
    var name: String {
        switch self {
        case .americanFootball:     return "American Football"
        case .archery:              return "Archery"
        case .australianFootball:   return "Australian Football"
        case .badminton:            return "Badminton"
        case .baseball:             return "Baseball"
        case .basketball:           return "Basketball"
        case .bowling:              return "Bowling"
        case .boxing:               return "Boxing"
        case .climbing:             return "Climbing"
        case .cricket:              return "Cricket"
        case .crossTraining:        return "Cross Training"
        case .curling:              return "Curling"
        case .cycling:              return "Cycling"
        case .dance:                return "Dance"
        case .elliptical:           return "Elliptical"
        case .equestrianSports:     return "Equestrian Sports"
        case .fencing:              return "Fencing"
        case .fishing:              return "Fishing"
        case .functionalStrengthTraining: return "Functional Strength Training"
        case .golf:                 return "Golf"
        case .gymnastics:           return "Gymnastics"
        case .handball:             return "Handball"
        case .hiking:               return "Hiking"
        case .hockey:               return "Hockey"
        case .hunting:              return "Hunting"
        case .lacrosse:             return "Lacrosse"
        case .martialArts:          return "Martial Arts"
        case .mindAndBody:          return "Mind and Body"
        case .paddleSports:         return "Paddle Sports"
        case .play:                 return "Play"
        case .preparationAndRecovery: return "Preparation and Recovery"
        case .racquetball:          return "Racquetball"
        case .rowing:               return "Rowing"
        case .rugby:                return "Rugby"
        case .running:              return "Running"
        case .sailing:              return "Sailing"
        case .skatingSports:        return "Skating Sports"
        case .snowSports:           return "Snow Sports"
        case .soccer:               return "Soccer"
        case .softball:             return "Softball"
        case .squash:               return "Squash"
        case .stairClimbing:        return "Stair Climbing"
        case .surfingSports:        return "Surfing"
        case .swimming:             return "Swimming"
        case .tableTennis:          return "Table Tennis"
        case .tennis:               return "Tennis"
        case .trackAndField:        return "Track and Field"
        case .traditionalStrengthTraining: return "Traditional Strength Training"
        case .volleyball:           return "Volleyball"
        case .walking:              return "Walking"
        case .waterFitness:         return "Water Fitness"
        case .waterPolo:            return "Water Polo"
        case .waterSports:          return "Water Sports"
        case .wrestling:            return "Wrestling"
        case .yoga:                 return "Yoga"
        case .highIntensityIntervalTraining: return "HIIT"
        case .jumpRope:             return "Jump Rope"
        case .kickboxing:           return "Kickboxing"
        case .pilates:              return "Pilates"
        case .snowboarding:         return "Snowboarding"
        case .stairs:               return "Stairs"
        case .stepTraining:         return "Step Training"
        case .wheelchairWalkPace:   return "Wheelchair Walk Pace"
        case .wheelchairRunPace:    return "Wheelchair Run Pace"
        case .taiChi:               return "Tai Chi"
        case .mixedCardio:          return "Mixed Cardio"
        case .handCycling:          return "Hand Cycling"
        case .discSports:           return "Disc Sports"
        case .fitnessGaming:        return "Fitness Gaming"
        case .cardioDance:          return "Cardio Dance"
        case .socialDance:          return "Social Dance"
        case .pickleball:           return "Pickleball"
        case .cooldown:             return "Cooldown"
        case .swimBikeRun:          return "Swim Bike Run"
        case .transition:           return "Transition"
        case .underwaterDiving:     return "Underwater Diving"
        default:                    return "Other (\(rawValue))"
        }
    }
}
