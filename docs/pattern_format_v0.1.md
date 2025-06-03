# Crochet Pattern JSON Format v0.1

This document describes the basic JSON format for representing crochet patterns.

## Root Object

The root of the JSON object will contain the following fields:

- `patternName`: (string) The name of the crochet pattern.
  - Example: `"Simple Circle"`
- `stitchType`: (string) The type of stitch used throughout the pattern. For this version, we assume all stitches in the pattern are of the same type.
  - Example: `"singleCrochet"`, `"doubleCrochet"`
- `rounds`: (array of objects) An array where each object represents a round in the crochet pattern.

## Round Object

Each object within the `rounds` array will have the following fields:

- `roundNumber`: (integer) The sequential number of the round, starting from 1.
- `stitches`: (integer) The total number of stitches to be made in this round.

## Example

```json
{
  "patternName": "Simple Circle",
  "stitchType": "singleCrochet",
  "rounds": [
    { "roundNumber": 1, "stitches": 6 },
    { "roundNumber": 2, "stitches": 12 },
    { "roundNumber": 3, "stitches": 18 }
  ]
}
```
