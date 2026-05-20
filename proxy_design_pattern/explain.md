# Proxy Design Pattern

## What is it?

Proxy is a structural pattern that provides a substitute or placeholder for another object. The proxy controls access to the original object, allowing you to perform something before or after the request reaches it.

## Types of Proxy

- Virtual Proxy: lazy initialization — creates expensive object only when needed
- Protection Proxy: access control — checks permissions before forwarding
- Remote Proxy: represents an object in a different address space
- Caching Proxy: caches results of expensive operations
- Logging Proxy: logs requests before forwarding

## When to Use

- Lazy initialization of a heavyweight object
- Access control / permission checks
- Caching expensive operation results
- Logging, monitoring, or auditing

## Example in `proxy.py`

A database query service with a caching proxy (TTL-based result cache), a logging proxy (audit trail), and a protection proxy (role-based access control). Proxies are stacked — request flows through all layers.
