# Technical Architectures Research

**Architectural patterns and technical implementations from open-source personal tracking systems.**

---

## Overview

This document covers technical architecture patterns identified in the research, including Local-First design, Event Sourcing, CRDTs, and data storage strategies.

---

## Local-First Architecture

### Definition

**Local-First** is a software design philosophy where:
1. Data lives primarily on the user's device
2. The application works fully offline
3. Cloud sync is optional, not required
4. User owns and controls their data

### Benefits

| Benefit | Description |
|---------|-------------|
| **Privacy** | Data never leaves device without user consent |
| **Longevity** | Data survives if service shuts down |
| **Performance** | Zero network latency for all operations |
| **Reliability** | Works without internet connection |
| **Ownership** | User has full control over their data |

### Storage Technologies

| Technology | Use Case | Example Projects |
|------------|----------|------------------|
| **SQLite** | Mobile/desktop, structured data | Loop, ActivityWatch |
| **IndexedDB** | Web applications, large datasets | Nomie, Perfice |
| **LocalStorage** | Simple key-value, small data | TrackLife (current) |
| **PouchDB** | Web with CouchDB sync | Various |
| **RxDB** | Reactive sync-capable DB | Various |

### TrackLife Migration Path

```
Current: LocalStorage (5-10MB limit, no query capability)
Target: IndexedDB via Dexie.js (unlimited, queryable, async)
```

---

## Event Sourcing

### Definition

**Event Sourcing** stores the sequence of events that led to current state, rather than just the current state itself.

### Traditional vs Event Sourcing

| Approach | What's Stored | Example |
|----------|---------------|---------|
| **Traditional** | Current state | `{ streak: 5, lastCompleted: "2026-02-14" }` |
| **Event Sourcing** | Sequence of events | `[{ type: "COMPLETED", date: "2026-02-14" }, ...]` |

### ActivityWatch's Bucket Model

ActivityWatch implements event sourcing through "Buckets":

```javascript
// Bucket structure
{
  "id": "aw-watcher-window_hostname",
  "type": "current-window",
  "client": "aw-watcher-window",
  "hostname": "user-machine",
  "events": [
    {
      "timestamp": "2026-02-14T10:00:00Z",
      "duration": 300,  // seconds
      "data": {
        "app": "Chrome",
        "title": "GitHub - ActivityWatch"
      }
    }
  ]
}
```

### Event Types for TrackLife

```javascript
// Habit events
{ type: "HABIT_CREATED", habitId: "uuid", timestamp: "2026-02-14T10:00:00Z", data: {...} }
{ type: "HABIT_COMPLETED", habitId: "uuid", timestamp: "2026-02-14T10:05:00Z" }
{ type: "HABIT_MISSED", habitId: "uuid", timestamp: "2026-02-14T10:05:00Z" }
{ type: "STREAK_FREEZE_USED", habitId: "uuid", timestamp: "2026-02-14T10:05:00Z" }
{ type: "HABIT_DELETED", habitId: "uuid", timestamp: "2026-02-14T10:05:00Z" }

// Task events
{ type: "TASK_CREATED", taskId: "uuid", timestamp: "...", data: {...} }
{ type: "TASK_COMPLETED", taskId: "uuid", timestamp: "..." }
{ type: "TASK_DELETED", taskId: "uuid", timestamp: "..." }

// Health events
{ type: "HEALTH_LOGGED", metric: "sleep", value: 7.5, unit: "hours", timestamp: "..." }
```

### Benefits of Event Sourcing

| Benefit | Description |
|---------|-------------|
| **Audit Trail** | Complete history of all changes |
| **Time Travel** | Reconstruct state at any point in time |
| **Debugging** | Understand exactly what happened |
| **Analytics** | Rich data for insights |
| **Undo/Redo** | Natural support for reversibility |

---

## CRDTs (Conflict-Free Replicated Data Types)

### The Sync Problem

When data exists on multiple devices:
1. User marks habit "done" on phone (offline)
2. User marks habit "skipped" on laptop (offline)
3. Both devices reconnect
4. **Conflict!** Which state wins?

### CRDT Solution

CRDTs are data structures that can be modified concurrently and automatically merge to a consistent state.

### Types of CRDTs

| Type | Use Case | Example |
|------|----------|---------|
| **Last-Write-Wins Register** | Simple values | Habit completion status |
| **G-Counter** | Grow-only counter | Total completions |
| **PN-Counter** | Increment/decrement counter | Streak count |
| **OR-Set** | Add/remove items | Task list |

### Libraries

| Library | Platform | Description |
|---------|----------|-------------|
| **Yjs** | JavaScript | CRDT framework for web |
| **Automerge** | JavaScript | JSON-like CRDT |
| **ElectricSQL** | SQLite → Postgres | Automatic sync |
| **Replicache** | JavaScript | Instant UI with sync |
| **PowerSync** | Multi-backend | Life OS dashboards |

### Implementation Example (Yjs)

```javascript
import * as Y from 'yjs';

const doc = new Y.Doc();
const habits = doc.getArray('habits');

// Add habit (works offline)
habits.push([{ id: '1', name: 'Exercise', completed: false }]);

// Sync with other devices
const syncProvider = new WebsocketProvider('wss://sync.server', 'room', doc);
```

---

## The Aggregator Pattern

### Definition

An aggregator ingests data from multiple sources, normalizes it, and provides a unified view.

### Ryot's Implementation

Ryot aggregates:
- Media (books, movies, games)
- Fitness (workouts, runs)
- Custom trackers

**Architecture:**
```
External APIs → Ingestion Layer → Normalizer → Database → GraphQL API → Frontend
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **Ingestion Layer** | Pull data from various sources |
| **Normalizer** | Transform to standard schema |
| **Polymorphic Storage** | Store diverse data types |
| **GraphQL API** | Flexible querying |

### TrackLife Application

```
HealthKit/Google Fit → Bridge App → API Endpoint → TrackLife DB
Manual Entry → UI → TrackLife DB
Wearable APIs → Ingestion Worker → TrackLife DB
```

---

## Data Storage Strategies

### TimescaleDB (for Time-Series)

For high-frequency data (sensors, heart rate):

```sql
-- Create hypertable (auto-partitioned by time)
CREATE TABLE sensor_data (
  time        TIMESTAMPTZ NOT NULL,
  sensor_id   INTEGER,
  value       DOUBLE PRECISION,
  attributes  JSONB
);

SELECT create_hypertable('sensor_data', 'time');

-- Efficient time-range queries
SELECT * FROM sensor_data 
WHERE time > NOW() - INTERVAL '7 days'
ORDER BY time DESC;
```

### JSONB for Flexibility

For varying sensor data:

```sql
-- Store arbitrary attributes
INSERT INTO sensor_data (time, sensor_id, value, attributes)
VALUES (
  NOW(),
  1,
  25.5,
  '{"battery": 80, "unit": "celsius", "location": "bedroom"}'::jsonb
);

-- Query nested attributes
SELECT * FROM sensor_data 
WHERE attributes->>'location' = 'bedroom';
```

---

## Open mHealth Schemas

### Overview

Open mHealth (OMH) provides standard schemas for health data, enabling interoperability.

### Schema Structure

```json
{
  "header": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "creation_date_time": "2026-02-14T10:00:00Z",
    "schema_id": {
      "namespace": "omh",
      "name": "step-count",
      "version": "2.0"
    },
    "acquisition_provenance": {
      "source_name": "TrackLife",
      "modality": "self-reported"
    }
  },
  "body": {
    "step_count": 6500,
    "effective_time_frame": {
      "time_interval": {
        "start_date_time": "2026-02-14T08:00:00Z",
        "end_date_time": "2026-02-14T20:00:00Z"
      }
    }
  }
}
```

### Available Schemas

| Schema | Purpose |
|--------|---------|
| `step-count` | Daily steps |
| `physical-activity` | Exercise sessions |
| `heart-rate` | BPM measurements |
| `sleep-duration` | Sleep tracking |
| `body-weight` | Weight measurements |
| `caloric-intake` | Food logging |

### TrackLife Schema Mapping

| TrackLife Data | OMH Schema |
|----------------|------------|
| Steps | `step-count` |
| Sleep hours | `sleep-duration` |
| Weight | `body-weight` |
| Exercise | `physical-activity` |
| Mood | Custom (extend OMH) |

---

## API Design Patterns

### GraphQL (Ryot Pattern)

```graphql
query GetHabits {
  habits(limit: 10, orderBy: { streak: DESC }) {
    id
    name
    streak
    score
    completions {
      date
      completed
    }
  }
}
```

### REST (Simple Pattern)

```
GET    /api/habits           # List all habits
POST   /api/habits           # Create habit
GET    /api/habits/:id       # Get single habit
PUT    /api/habits/:id       # Update habit
DELETE /api/habits/:id       # Delete habit
POST   /api/habits/:id/complete  # Mark complete
```

### Webhook Pattern

```javascript
// External service sends data
POST /api/webhook/:source
{
  "source": "healthkit-bridge",
  "event": "steps",
  "data": {
    "count": 8500,
    "date": "2026-02-14"
  },
  "signature": "hmac-sha256=..."
}
```

---

## Performance Considerations

### IndexedDB Best Practices

```javascript
// Use Dexie.js for easier IndexedDB
import Dexie from 'dexie';

const db = new Dexie('TrackLifeDB');
db.version(1).stores({
  habits: '++id, name, createdAt',
  completions: '++id, habitId, date, completed',
  events: '++id, type, timestamp'
});

// Bulk operations for performance
await db.habits.bulkPut(habitsArray);

// Indexed queries
const recentCompletions = await db.completions
  .where('date').above('2026-02-01')
  .toArray();
```

### Query Optimization

| Technique | Use Case |
|-----------|----------|
| **Indexing** | Frequent query fields |
| **Bulk Operations** | Batch inserts/updates |
| **Lazy Loading** | Large datasets |
| **Pagination** | Long lists |
| **Caching** | Computed values |

---

## Implementation Checklist

### Phase 1: Storage Foundation

- [ ] Add Dexie.js library
- [ ] Define IndexedDB schema
- [ ] Create migration script from LocalStorage
- [ ] Update all modules to use IndexedDB
- [ ] Add event sourcing layer

### Phase 2: Data Standards

- [ ] Implement OMH schema validation
- [ ] Create schema migration utilities
- [ ] Add data export in OMH format

### Phase 3: Sync Preparation

- [ ] Evaluate CRDT library (Yjs/Automerge)
- [ ] Design sync protocol
- [ ] Create conflict resolution strategy

---

## References

- Local-First Software: https://www.inkandswitch.com/essay/local-first/
- ActivityWatch Documentation: https://docs.activitywatch.net/
- Open mHealth: https://www.openmhealth.org/
- Dexie.js: https://dexie.org/
- Yjs: https://yjs.dev/

---

## Cross-References

| Related Document | Content |
|------------------|---------|
| [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md) | Overview of all research |
| [OPEN_SOURCE_PROJECTS.md](OPEN_SOURCE_PROJECTS.md) | Project implementations |
| [docs/schemas/EVENT_SCHEMA.md](../schemas/EVENT_SCHEMA.md) | Event schema spec |
| [docs/guides/INDEXEDDB_MIGRATION.md](../guides/INDEXEDDB_MIGRATION.md) | Migration guide |

---

*Last updated: February 2026*