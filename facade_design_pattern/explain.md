# Facade Design Pattern

## What is it?

The Facade pattern is a structural design pattern that provides a simplified interface to a complex subsystem. It doesn't hide the subsystem — it just gives you a clean, easy entry point so you don't have to deal with all the moving parts directly.

Think of it as a "front desk" — you talk to one person, and they coordinate everything behind the scenes.

## When to Use

- You have a complex subsystem with many classes and you want a simple interface over it
- You want to layer your system and provide entry points to each layer
- You want to decouple clients from subsystem internals
- You're wrapping a legacy system or third-party library with a cleaner API

## Structure

```
Client → Facade → SubsystemA
                → SubsystemB
                → SubsystemC
                → SubsystemD
```

- Facade: The single entry point. Knows which subsystem classes to call and in what order
- Subsystems: Do the actual work. They don't know the facade exists
- Client: Only talks to the Facade, never to subsystems directly

## Facade vs Adapter vs Proxy

| | Facade | Adapter | Proxy |
|---|---|---|---|
| Purpose | Simplify a complex interface | Convert one interface to another | Control access to an object |
| Number of classes | Wraps many | Wraps one | Wraps one |
| Changes interface? | Yes (simplifies) | Yes (translates) | No (same interface) |

## Real-World Analogy

Booking a holiday package. You call one travel agent (Facade) who handles flights, hotels, car rentals, and insurance separately. You don't call each provider yourself — the agent coordinates it all.

## Pros

- Isolates clients from subsystem complexity
- Reduces dependencies between client code and internals
- Easy to swap or refactor subsystems without touching client code

## Cons

- The facade can become a "god object" if it takes on too much responsibility
- Doesn't prevent clients from using subsystems directly if they need to

## Example in `facade.py`

Models a home theater system where:
- Subsystems: `Amplifier`, `DVDPlayer`, `Projector`, `StreamingService`, `Lights`, `AirConditioner`, `SurroundSound`
- Each has its own complex API
- `HomeTheaterFacade` provides simple methods: `watch_movie()`, `end_movie()`, `watch_stream()`, `party_mode()`
- The client calls one method and all subsystems coordinate automatically
- Includes state tracking, error handling, and scene presets
