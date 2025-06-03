import numpy as np

# Assume a constant value for stitch width/height for now.
# This value would affect the overall size of the generated circle.
STITCH_GAUGE = 0.5 # Arbitrary unit, e.g., cm per stitch width/height

def generate_shape_coordinates(parsed_pattern):
    """
    Generates 3D coordinates for stitches in a crochet pattern,
    currently supporting only flat circles.

    Args:
        parsed_pattern: A dictionary representing the parsed crochet pattern,
                        as returned by `parser.parse_pattern`.

    Returns:
        A list of lists, where each inner list contains [x, y, z]
        coordinates for a stitch.
    """
    all_stitch_coordinates = []
    current_radius = 0 # Initial radius

    # Validate basic structure from parser
    if not all(k in parsed_pattern for k in ["patternName", "stitchType", "rounds"]):
        raise ValueError("Parsed pattern is missing essential keys.")
    if not isinstance(parsed_pattern["rounds"], list) or not parsed_pattern["rounds"]:
        raise ValueError("'rounds' must be a non-empty list.")

    # For a flat circle, the increase in radius per round is related to the stitch gauge.
    # This is a simplification. In reality, it depends on stitch height.
    radius_increase_per_round = STITCH_GAUGE

    for round_data in parsed_pattern["rounds"]:
        if not all(k in round_data for k in ["roundNumber", "stitches"]):
            raise ValueError("Round data is missing 'roundNumber' or 'stitches'.")

        num_stitches_in_round = round_data["stitches"]
        if num_stitches_in_round <= 0:
            # Skip rounds with no stitches or handle as an error if preferred
            print(f"Warning: Round {round_data['roundNumber']} has {num_stitches_in_round} stitches. Skipping.")
            continue

        # For the first round, the radius is small, essentially the first set of stitches forming a small ring or point.
        # For subsequent rounds, the radius increases.
        if round_data["roundNumber"] == 1 and num_stitches_in_round > 0 :
             # Estimate radius for the first round based on circumference
            current_radius = (num_stitches_in_round * STITCH_GAUGE) / (2 * np.pi)
        elif round_data["roundNumber"] > 1:
            # Increase radius for subsequent rounds.
            # A more accurate model might involve the height of the previous round's stitches.
            # For simplicity, let's assume the new radius is such that the new stitches fit.
            # The circumference of the new round is num_stitches_in_round * STITCH_GAUGE.
            # So, new_radius = (num_stitches_in_round * STITCH_GAUGE) / (2 * np.pi)
            # This means current_radius should effectively be the radius of the *previous* round's outer edge.
            # Let's adjust the radius based on the previous round's stitch count or a fixed increment.
            # For a simple flat circle that grows, the radius of round N is proportional to N.
            # Or, more directly, the radius is determined by the circumference needed for its stitches.
            current_radius = (num_stitches_in_round * STITCH_GAUGE) / (2 * np.pi)


        round_coordinates = []
        for i in range(num_stitches_in_round):
            angle = (2 * np.pi / num_stitches_in_round) * i
            x = current_radius * np.cos(angle)
            y = current_radius * np.sin(angle)
            z = 0  # Flat circle
            # Convert numpy floats to standard Python floats and round
            round_coordinates.append([round(float(x), 3), round(float(y), 3), round(float(z), 3)])

        all_stitch_coordinates.extend(round_coordinates)
        # For the next round, the radius will be larger.
        # This simple model updates radius based on the circumference of the current round,
        # which is suitable if we imagine stitches being placed around a center point.

    return all_stitch_coordinates

if __name__ == "__main__":
    print("Testing shape generator...")

    # Sample parsed pattern (mimicking output from simple_circle.json)
    sample_pattern_data = {
        "patternName": "Simple Circle Test",
        "stitchType": "singleCrochet",
        "rounds": [
            {"roundNumber": 1, "stitches": 6},
            {"roundNumber": 2, "stitches": 12},
            {"roundNumber": 3, "stitches": 18},
            {"roundNumber": 4, "stitches": 24}
        ]
    }
    print(f"\n--- Testing with sample pattern: {sample_pattern_data['patternName']} ---")
    try:
        coordinates = generate_shape_coordinates(sample_pattern_data)
        print(f"Generated {len(coordinates)} coordinates.")
        # Print first few and last few coordinates as a sample
        if len(coordinates) > 10:
            print("Sample coordinates (first 5):")
            for i in range(5):
                print(coordinates[i])
            print("...")
            print("Sample coordinates (last 5):")
            for i in range(len(coordinates) - 5, len(coordinates)):
                print(coordinates[i])
        else:
            for coord in coordinates:
                print(coord)
    except ValueError as e:
        print(f"Error generating coordinates: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Test with empty rounds
    print("\n--- Testing with empty rounds ---")
    empty_rounds_pattern = {
        "patternName": "Empty Rounds Test",
        "stitchType": "sc",
        "rounds": []
    }
    try:
        generate_shape_coordinates(empty_rounds_pattern)
    except ValueError as e:
        print(f"Caught expected error: {e}")


    # Test with round with zero stitches
    print("\n--- Testing with round with zero stitches ---")
    zero_stitches_pattern = {
        "patternName": "Zero Stitches Test",
        "stitchType": "sc",
        "rounds": [
            {"roundNumber": 1, "stitches": 6},
            {"roundNumber": 2, "stitches": 0},
            {"roundNumber": 3, "stitches": 12}
        ]
    }
    try:
        coords = generate_shape_coordinates(zero_stitches_pattern)
        print(f"Generated {len(coords)} coordinates (should skip round 2).")
        # Expected: 6 + 12 = 18 coordinates
        # Round 1: radius for 6 stitches
        # Round 3: radius for 12 stitches (independent of round 2)
        # Check if the count is 18
        if len(coords) == 18:
             print("Correct number of coordinates generated.")
        else:
             print(f"Incorrect number of coordinates: {len(coords)}, expected 18.")

    except ValueError as e:
        print(f"Error: {e}")


    print("\nShape generator tests finished.")
