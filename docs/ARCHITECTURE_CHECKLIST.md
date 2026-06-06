# Architecture Checklist

Before merging code:

## Ownership

- Is the module in the correct domain?

## Dependency

- Does it violate dependency rules?

## Service Layer

- Is dashboard calling services only?

## Duplication

- Does functionality already exist?

## Logging

- Uses core.logger?

## Config

- Uses core.config?

## Testing

- Has unit tests?
