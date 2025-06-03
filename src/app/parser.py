import json

def parse_pattern(pattern_string):
    """
    Parses a crochet pattern string (JSON) and validates its structure.

    Args:
        pattern_string: A string containing the JSON pattern data.

    Returns:
        A dictionary representing the parsed pattern.

    Raises:
        ValueError: If the pattern string is invalid JSON or if the
                    pattern structure is not as expected.
    """
    try:
        pattern_data = json.loads(pattern_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

    # Basic validation for required keys
    required_keys = ["patternName", "stitchType", "rounds"]
    for key in required_keys:
        if key not in pattern_data:
            raise ValueError(f"Missing required key: '{key}'")

    # Validate 'patternName' is a string
    if not isinstance(pattern_data["patternName"], str):
        raise ValueError("'patternName' must be a string.")

    # Validate 'stitchType' is a string
    if not isinstance(pattern_data["stitchType"], str):
        raise ValueError("'stitchType' must be a string.")

    # Validate 'rounds' is a list
    if not isinstance(pattern_data["rounds"], list):
        raise ValueError("'rounds' must be a list.")

    if not pattern_data["rounds"]:
        raise ValueError("'rounds' list cannot be empty.")

    # Validate each round in 'rounds'
    for i, round_item in enumerate(pattern_data["rounds"]):
        if not isinstance(round_item, dict):
            raise ValueError(f"Each item in 'rounds' must be a dictionary. Found: {type(round_item)} at index {i}.")

        if "roundNumber" not in round_item:
            raise ValueError(f"Missing 'roundNumber' in round item at index {i}.")
        if not isinstance(round_item["roundNumber"], int):
            raise ValueError(f"'roundNumber' must be an integer in round item at index {i}. Found: {type(round_item['roundNumber'])}")

        if "stitches" not in round_item:
            raise ValueError(f"Missing 'stitches' in round item at index {i}.")
        if not isinstance(round_item["stitches"], int):
            raise ValueError(f"'stitches' must be an integer in round item at index {i}. Found: {type(round_item['stitches'])}")

    return pattern_data

if __name__ == "__main__":
    # Test section
    print("Testing pattern parser...")

    # Test with a valid pattern file
    valid_pattern_file = "patterns/simple_circle.json" # Relative to project root
    print(f"\n--- Testing with valid file: {valid_pattern_file} ---")
    try:
        with open(valid_pattern_file, 'r') as f:
            valid_pattern_content = f.read()
        parsed_pattern = parse_pattern(valid_pattern_content)
        print("Pattern parsed successfully:")
        print(json.dumps(parsed_pattern, indent=2))
    except FileNotFoundError:
        print(f"Error: Test pattern file not found at {valid_pattern_file}")
        print("Please ensure 'patterns/simple_circle.json' exists at the root of the project.")
    except ValueError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Test with invalid JSON string
    print("\n--- Testing with invalid JSON string ---")
    invalid_json_string = '{"patternName": "Test", "stitchType": "dc", "rounds": [}' # Malformed JSON
    try:
        parse_pattern(invalid_json_string)
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Test with missing 'patternName'
    print("\n--- Testing with missing 'patternName' ---")
    missing_key_pattern = {"stitchType": "sc", "rounds": [{"roundNumber": 1, "stitches": 5}]}
    try:
        parse_pattern(json.dumps(missing_key_pattern))
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Test with 'rounds' not a list
    print("\n--- Testing with 'rounds' not a list ---")
    rounds_not_list_pattern = {"patternName": "Test", "stitchType": "sc", "rounds": "not a list"}
    try:
        parse_pattern(json.dumps(rounds_not_list_pattern))
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Test with empty 'rounds' list
    print("\n--- Testing with empty 'rounds' list ---")
    empty_rounds_pattern = {"patternName": "Test", "stitchType": "sc", "rounds": []}
    try:
        parse_pattern(json.dumps(empty_rounds_pattern))
    except ValueError as e:
        print(f"Caught expected error: {e}")


    # Test with missing 'stitches' in a round
    print("\n--- Testing with missing 'stitches' in a round ---")
    missing_stitches_pattern = {
        "patternName": "Test",
        "stitchType": "sc",
        "rounds": [{"roundNumber": 1}] # Missing "stitches"
    }
    try:
        parse_pattern(json.dumps(missing_stitches_pattern))
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Test with 'roundNumber' not an integer
    print("\n--- Testing with 'roundNumber' not an integer ---")
    round_number_not_int_pattern = {
        "patternName": "Test",
        "stitchType": "sc",
        "rounds": [{"roundNumber": "1", "stitches": 10}] # "1" is a string
    }
    try:
        parse_pattern(json.dumps(round_number_not_int_pattern))
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\nParser tests finished.")
