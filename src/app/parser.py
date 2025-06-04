import json

# Define allowed stitch types for v0.2 format
ALLOWED_STITCH_TYPES_V0_2 = [
    "sc", "inc", "dec", "dc", "hdc", "tr", "slst", "ch", "mr", "blo", "flo"
    # Note: "blo", "flo" might be combined with others e.g. "sc_blo".
    # For now, keeping them separate. Parser might need enhancement for combined types later.
]

def parse_pattern(pattern_string):
    """
    Parses a crochet pattern string (JSON) and validates its structure
    according to pattern format v0.2.

    Args:
        pattern_string: A string containing the JSON pattern data.

    Returns:
        A dictionary representing the parsed pattern (v0.2 structure).

    Raises:
        ValueError: If the pattern string is invalid JSON or if the
                    pattern structure is not as expected for v0.2.
    """
    try:
        pattern_data = json.loads(pattern_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

    # Basic validation for required top-level keys
    if "patternName" not in pattern_data:
        raise ValueError("Missing required key: 'patternName'")
    if not isinstance(pattern_data["patternName"], str):
        raise ValueError("'patternName' must be a string.")

    if "rounds" not in pattern_data:
        raise ValueError("Missing required key: 'rounds'")
    if not isinstance(pattern_data["rounds"], list):
        raise ValueError("'rounds' must be a list.")
    # 'stitchType' is optional/deprecated in v0.2, so no strict check on it.

    if not pattern_data["rounds"]:
        # While an empty pattern (no rounds) could be valid in some contexts,
        # for visualization, it's not useful. Let's expect at least one round.
        # Or, this could be allowed and handled by the shape generator.
        # For now, let's keep the previous behavior of disallowing empty "rounds" list.
        # Update: Previous parser raised error for empty rounds list. This was for v0.1 structure.
        # For v0.2, an empty rounds list might mean an empty pattern, which is valid JSON.
        # The shape generator should handle it.
        # However, the prompt for v0.1 parser said "if not pattern_data["rounds"]: raise ValueError"
        # Let's re-evaluate based on current subtask: validate that `stitches` is a non-empty list *within* a round.
        # An empty `rounds` array itself is structurally valid for the pattern format.
        pass # Allow empty "rounds" list at top level.

    # Validate each round in 'rounds'
    for i, round_item in enumerate(pattern_data["rounds"]):
        if not isinstance(round_item, dict):
            raise ValueError(f"Each item in 'rounds' must be a dictionary. Found: {type(round_item)} at round index {i}.")

        if "roundNumber" not in round_item:
            raise ValueError(f"Missing 'roundNumber' in round item at index {i}.")
        if not isinstance(round_item["roundNumber"], int):
            raise ValueError(f"'roundNumber' must be an integer in round item at index {i}. Found: {type(round_item['roundNumber'])}")

        if "stitches" not in round_item:
            raise ValueError(f"Missing 'stitches' array in round item for roundNumber {round_item.get('roundNumber', i+1)} (index {i}).")
        if not isinstance(round_item["stitches"], list):
            raise ValueError(f"'stitches' must be a list in round item for roundNumber {round_item.get('roundNumber', i+1)} (index {i}). Found: {type(round_item['stitches'])}")

        if not round_item["stitches"]: # Check for non-empty list of stitch objects
            raise ValueError(f"'stitches' list cannot be empty in round item for roundNumber {round_item.get('roundNumber', i+1)} (index {i}).")

        # Validate each stitch object in the 'stitches' list for this round
        for j, stitch_obj in enumerate(round_item["stitches"]):
            if not isinstance(stitch_obj, dict):
                raise ValueError(f"Each stitch entry must be an object. Found: {type(stitch_obj)} at stitch index {j} in roundNumber {round_item.get('roundNumber', i+1)}.")

            if "type" not in stitch_obj:
                raise ValueError(f"Stitch object missing 'type' key at stitch index {j} in roundNumber {round_item.get('roundNumber', i+1)}.")
            if not isinstance(stitch_obj["type"], str):
                raise ValueError(f"Stitch 'type' must be a string. Found: {type(stitch_obj['type'])} at stitch index {j} in roundNumber {round_item.get('roundNumber', i+1)}.")

            if stitch_obj["type"] not in ALLOWED_STITCH_TYPES_V0_2:
                # Allow for combined types like "sc_blo" if we adopt a convention
                # For now, strict check.
                is_combined = False
                if "_" in stitch_obj["type"]:
                    base_type, modifier = stitch_obj["type"].split("_", 1)
                    if base_type in ALLOWED_STITCH_TYPES_V0_2 and modifier in ["blo", "flo"]:
                        is_combined = True

                if not is_combined:
                    raise ValueError(f"Invalid stitch 'type': \"{stitch_obj['type']}\". Allowed types are: {ALLOWED_STITCH_TYPES_V0_2} (and type_modifier combinations like sc_blo). Stitch index {j} in roundNumber {round_item.get('roundNumber', i+1)}.")

            # Could add more validation here, e.g. for stitch-specific attributes if format evolves further.

    return pattern_data

if __name__ == "__main__":
    print("Testing pattern parser (v0.2 format)...")

    # Test with valid v0.2 pattern files
    valid_patterns_paths = [
        "patterns/simple_circle.json",    # Updated to v0.2
        "patterns/basic_sphere_v0.2.json"
    ]
    for pattern_path in valid_patterns_paths:
        print(f"\n--- Testing with valid file: {pattern_path} ---")
        try:
            with open(pattern_path, 'r') as f:
                pattern_content = f.read()
            parsed_pattern = parse_pattern(pattern_content)
            print(f"Pattern '{parsed_pattern['patternName']}' parsed successfully.")
            # print(json.dumps(parsed_pattern, indent=2)) # Optionally print full parsed pattern
        except FileNotFoundError:
            print(f"Error: Test pattern file not found at {pattern_path}")
        except ValueError as e:
            print(f"Validation Error for {pattern_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with {pattern_path}: {e}")

    print("\n--- Testing combined stitch types (e.g., sc_blo) ---")
    combined_type_pattern_valid = {
        "patternName": "Combined Type Test",
        "rounds": [{
            "roundNumber": 1,
            "stitches": [{"type": "sc_blo"}, {"type": "inc_flo"}]
        }]
    }
    try:
        parse_pattern(json.dumps(combined_type_pattern_valid))
        print("Combined stitch types 'sc_blo', 'inc_flo' parsed successfully.")
    except ValueError as e:
        print(f"Error parsing combined stitch types: {e}")


    # --- Test cases for invalid v0.2 patterns ---

    print("\n--- Testing invalid patterns (v0.2 format) ---")

    test_cases_invalid = [
        {
            "name": "Missing 'stitches' array in a round",
            "pattern": {"patternName": "Test", "rounds": [{"roundNumber": 1}]} # Missing "stitches"
        },
        {
            "name": "Empty 'stitches' array in a round",
            "pattern": {"patternName": "Test", "rounds": [{"roundNumber": 1, "stitches": []}]}
        },
        {
            "name": "Invalid stitch 'type'",
            "pattern": {"patternName": "Test", "rounds": [{"roundNumber": 1, "stitches": [{"type": "foo"}]}]}
        },
        {
            "name": "Stitch object missing 'type' key",
            "pattern": {"patternName": "Test", "rounds": [{"roundNumber": 1, "stitches": [{"not_type": "sc"}]}]}
        },
        {
            "name": "Stitch 'type' not a string",
            "pattern": {"patternName": "Test", "rounds": [{"roundNumber": 1, "stitches": [{"type": 123}]}]}
        },
        {
            "name": "'stitches' not a list",
            "pattern": {"patternName": "Test", "rounds": [{"roundNumber": 1, "stitches": "not_a_list"}]}
        },
        {
            "name": "Round item not a dictionary",
            "pattern": {"patternName": "Test", "rounds": ["not_a_dictionary"]}
        },
        {
            "name": "Top-level 'rounds' not a list",
            "pattern": {"patternName": "Test", "rounds": "not_a_list"}
        },
        {
            "name": "Missing 'patternName'",
            "pattern": {"rounds": [{"roundNumber": 1, "stitches": [{"type": "sc"}]}]}
        }
    ]

    for test_case in test_cases_invalid:
        print(f"\nTesting: {test_case['name']}")
        try:
            parse_pattern(json.dumps(test_case['pattern']))
            print(f"Error: Expected ValueError for '{test_case['name']}', but parsing succeeded.")
        except ValueError as e:
            print(f"Caught expected ValueError: {e}")
        except Exception as e:
            print(f"Caught unexpected error for '{test_case['name']}': {e}")

    print("\n--- Testing with empty top-level 'rounds' list (should be valid) ---")
    empty_rounds_pattern = {"patternName": "Empty Rounds", "rounds": []}
    try:
        parsed = parse_pattern(json.dumps(empty_rounds_pattern))
        print(f"Pattern '{parsed['patternName']}' with empty 'rounds' list parsed successfully.")
    except ValueError as e:
        print(f"Error: Expected empty 'rounds' list to be valid, but got ValueError: {e}")


    print("\nParser tests (v0.2) finished.")
