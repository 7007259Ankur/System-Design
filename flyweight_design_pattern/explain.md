# Flyweight Design Pattern

## What is it?

Flyweight is a structural pattern that lets you fit more objects into available RAM by sharing common state among multiple objects instead of keeping all data in each object.

Split object state into:
- Intrinsic state: shared, immutable, stored in the flyweight
- Extrinsic state: unique per object, passed in by the client

## When to Use

- Your app needs a huge number of similar objects
- Objects consume too much RAM
- Most object state can be made extrinsic (passed in rather than stored)

## Example in `flyweight.py`

A particle system for a game — thousands of bullets, explosions, debris. The flyweight stores shared data (texture, color, sprite). The extrinsic state (position, velocity, direction) is passed at render time. A FlyweightFactory caches and reuses flyweights.
