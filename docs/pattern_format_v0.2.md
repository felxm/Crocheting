# Crochet Pattern JSON Format v0.2

This document describes the JSON format for representing crochet patterns, version 0.2. This version introduces detailed stitch information within each round.

## Root Object

The root of the JSON object will contain the following fields:

- `patternName`: (string) The name of the crochet pattern.
  - Example: `"Amigurumi Sphere"`
- `stitchType`: (string) This field is **deprecated** in v0.2 as stitch types are now specified per stitch. It may be kept for backward compatibility or general information, but is no longer the primary source for stitch type information.
  - Example: `"mixed"`
- `rounds`: (array of objects) An array where each object represents a round in the crochet pattern.

## Round Object

Each object within the `rounds` array will have the following fields:

- `roundNumber`: (integer) The sequential number of the round, starting from 1.
- `stitches`: (array of objects) An array where each object represents a single stitch or stitch operation (like an increase or decrease).

## Stitch Object

Each object within a round's `stitches` array will have the following field:

- `type`: (string) Defines the type of the stitch or operation.
  - Common examples:
    - `"sc"`: Single Crochet
    - `"inc"`: Increase (typically two single crochets in the same stitch)
    - `"dec"`: Decrease (typically a single crochet two together)
    - `"dc"`: Double Crochet
    - `"hdc"`: Half Double Crochet
    - `"tr"`: Treble Crochet
    - `"slst"`: Slip Stitch
    - `"ch"`: Chain stitch
    - `"mr"`: Magic Ring (often implied at the start, but can be explicit)
    - `"blo"`: Back Loop Only (can be a modifier or combined, e.g. "sc_blo")
    - `"flo"`: Front Loop Only (can be a modifier or combined)
  - Note: The interpretation of "inc" and "dec" in terms of actual stitch count increase/decrease will be handled by the parser/generator. For example, one "inc" object contributes to one operation but results in +1 stitch to the round's total effective stitch count for the *next* round's basis.

## Example of a Round

```json
{
  "roundNumber": 1,
  "stitches": [
    { "type": "sc" },
    { "type": "sc" },
    { "type": "sc" },
    { "type": "sc" },
    { "type": "sc" },
    { "type": "sc" }
  ]
}
```

```json
{
  "roundNumber": 2,
  "stitches": [
    { "type": "sc" },
    { "type": "inc" },
    { "type": "sc" },
    { "type": "inc" },
    { "type": "sc" },
    { "type": "inc" },
    { "type": "sc" },
    { "type": "inc" },
    { "type": "sc" },
    { "type": "inc" },
    { "type": "sc" },
    { "type": "inc" }
  ]
}
```
*(The above round 2 example represents (sc, inc) repeated 6 times, where each "inc" is one operation but implies two stitches were worked into one stitch of the previous round).*

## Full Pattern Example (Conceptual)

```json
{
  "patternName": "Simple Piece v0.2",
  "stitchType": "mixed", // Deprecated but informative
  "rounds": [
    {
      "roundNumber": 1,
      "stitches": [
        { "type": "sc" }, { "type": "sc" }, { "type": "sc" },
        { "type": "sc" }, { "type": "sc" }, { "type": "sc" }
      ]
    },
    {
      "roundNumber": 2,
      "stitches": [
        { "type": "inc" }, { "type": "inc" }, { "type": "inc" },
        { "type": "inc" }, { "type": "inc" }, { "type": "inc" }
      ]
    }
    // ... more rounds
  ]
}
```
