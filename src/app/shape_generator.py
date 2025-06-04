import numpy as np

# STITCH_GAUGE represents approximate width of a single crochet stitch.
# This helps determine radius/circumference.
STITCH_GAUGE = 0.5  # Arbitrary unit, e.g., cm per stitch width

# Define properties for recognized stitch types.
# - height: How much it contributes to the Y-axis increase of the piece.
# - consumes: How many stitches from the previous round this operation works into.
# - produces: How many effective stitches this operation creates for the *next* round to work into.
# - width_factor: Multiplier for STITCH_GAUGE for this stitch, affecting spacing.
#                 (e.g. a 'dc' might be slightly wider than an 'sc')
STITCH_PROPERTIES = {
    "sc":   {"height": 1.0 * STITCH_GAUGE, "consumes": 1, "produces": 1, "width_factor": 1.0},
    "inc":  {"height": 1.0 * STITCH_GAUGE, "consumes": 1, "produces": 2, "width_factor": 1.0}, # Typically 2 sc in one st
    "dec":  {"height": 1.0 * STITCH_GAUGE, "consumes": 2, "produces": 1, "width_factor": 1.0}, # Typically sc2tog
    "slst": {"height": 0.2 * STITCH_GAUGE, "consumes": 1, "produces": 1, "width_factor": 0.8}, # Slip stitch is short and tight
    "hdc":  {"height": 1.5 * STITCH_GAUGE, "consumes": 1, "produces": 1, "width_factor": 1.2},
    "dc":   {"height": 2.0 * STITCH_GAUGE, "consumes": 1, "produces": 1, "width_factor": 1.5},
    "tr":   {"height": 3.0 * STITCH_GAUGE, "consumes": 1, "produces": 1, "width_factor": 2.0},
    "ch":   {"height": 0.8 * STITCH_GAUGE, "consumes": 0, "produces": 1, "width_factor": 1.0}, # Chain produces a stitch for next round, consumes 0 from prev. round
                                                                                         # Height is tricky, depends on tension. Width is for layout if in a round.
    "mr":   {"height": 0.0, "consumes": 0, "produces": 0, "width_factor": 0.0} # Magic Ring itself isn't a stitch with geometry here.
    # Modifiers like _blo, _flo are handled by splitting stitch type string.
}
# Default properties for unknown stitch types
DEFAULT_STITCH_PROPS = {"height": 1.0 * STITCH_GAUGE, "consumes": 1, "produces": 1, "width_factor": 1.0}


def get_stitch_props(stitch_type_str):
    base_type = stitch_type_str.split("_")[0] # e.g., "sc_blo" -> "sc"
    return STITCH_PROPERTIES.get(base_type, DEFAULT_STITCH_PROPS)


def generate_shape_coordinates(parsed_pattern):
    """
    Generates 3D coordinates for stitches in a crochet pattern (v0.2 format).
    Attempts to model height and approximate 3D shape.

    Args:
        parsed_pattern: A dictionary representing the parsed crochet pattern (v0.2).

    Returns:
        A list of lists, where each inner list contains [x, y, z] coordinates.
    """
    all_stitch_visual_coordinates = [] # Coordinates for each visual stitch marker

    # State variables
    current_y_level = 0.0
    # Stores the [x,y,z] for each stitch *produced* in the previous round,
    # which form the base for the current round.
    previous_round_base_coords = []
    # Number of stitches the current round will work into.
    num_base_stitches_for_current_round = 0

    if not parsed_pattern or "rounds" not in parsed_pattern or not isinstance(parsed_pattern["rounds"], list):
        raise ValueError("Invalid pattern format or missing 'rounds'.")

    for round_idx, round_data in enumerate(parsed_pattern["rounds"]):
        if "stitches" not in round_data or not isinstance(round_data["stitches"], list):
            raise ValueError(f"Round {round_data.get('roundNumber', round_idx + 1)} is missing 'stitches' list.")

        current_round_stitch_instructions = round_data["stitches"]
        if not current_round_stitch_instructions:
            print(f"Warning: Round {round_data.get('roundNumber', round_idx + 1)} has no stitch instructions. Skipping.")
            continue

        # --- Calculate properties for the current round ---
        current_round_avg_height = 0
        current_round_total_produced_stitches = 0
        current_round_total_consumed_stitches = 0

        for stitch_instr in current_round_stitch_instructions:
            props = get_stitch_props(stitch_instr["type"])
            current_round_avg_height += props["height"]
            current_round_total_produced_stitches += props["produces"]
            current_round_total_consumed_stitches += props["consumes"]

        if current_round_stitch_instructions:
            current_round_avg_height /= len(current_round_stitch_instructions)
        else: # Should not happen due to check above, but for safety
            current_round_avg_height = STITCH_GAUGE


        # --- Handle the very first round (e.g., magic ring) ---
        if round_idx == 0:
            # Assume first round forms a flat circle at y=0.
            # The "radius" is based on the stitches *produced* by this first round.
            # This is a common start for amigurumi.
            num_base_stitches_for_current_round = current_round_total_produced_stitches # Stitches worked into nothing, e.g. MR
            current_y_level = 0.0 # First round starts at y=0
            # If it's chains for a foundation row, this logic would need to be different (linear layout)
            # For now, assume circular start.
            if any(instr["type"] == "ch" for instr in current_round_stitch_instructions) and \
               not any(instr["type"] == "sc" for instr in current_round_stitch_instructions): # Primitive chain row check
                # Basic linear layout for a starting chain row
                current_x_offset = 0.0
                temp_next_round_base_coords = []
                for stitch_instr in current_round_stitch_instructions:
                    props = get_stitch_props(stitch_instr["type"])
                    # Place one visual marker per produced stitch for chains
                    for _ in range(props["produces"]):
                        coord = [round(current_x_offset, 3), round(current_y_level, 3), 0.0]
                        all_stitch_visual_coordinates.append(coord)
                        temp_next_round_base_coords.append(coord)
                        current_x_offset += props["width_factor"] * STITCH_GAUGE
                previous_round_base_coords = temp_next_round_base_coords
                num_base_stitches_for_current_round = current_round_total_produced_stitches # For the *next* round
                current_y_level += current_round_avg_height # Chains do have some height
                continue # Move to next round

        elif not previous_round_base_coords: # Should not happen after round 0 unless round 0 was skipped
             raise ValueError("Previous round data is missing for stitch placement.")


        # --- Determine radius for placing current round's stitches ---
        # Radius is based on the circumference needed for the stitches of the *previous* round.
        # Stitches are placed *onto* the structure formed by the previous round.
        if num_base_stitches_for_current_round == 0: # Avoid division by zero if prev round produced nothing
            current_radius = STITCH_GAUGE
        else:
            # Calculate effective gauge/width from previous round for radius calculation.
            # This is simplified; a better model would use actual x,z coords of previous_round_base_coords.
            # For now, using the count of stitches that form the base.
            current_radius = (num_base_stitches_for_current_round * STITCH_GAUGE) / (2 * np.pi)

        current_stitch_idx_in_base = 0 # Index for consuming stitches from previous_round_base_coords
        temp_next_round_base_coords = [] # Stores coords for stitches *produced* in this round

        for stitch_instr_idx, stitch_instr in enumerate(current_round_stitch_instructions):
            props = get_stitch_props(stitch_instr["type"])

            # Determine anchor point(s) from previous round for this stitch operation
            # This is simplified: assumes stitches are consumed sequentially from prev round's perimeter.
            # For decreases, it would average positions of consumed stitches.
            # For increases, it uses one base stitch's position.

            avg_x_base = 0
            avg_z_base = 0
            num_consumed_for_avg = 0

            if num_base_stitches_for_current_round > 0: # If there's a base to work into
                for _ in range(props["consumes"]):
                    if current_stitch_idx_in_base < num_base_stitches_for_current_round:
                        # Use angular placement based on the *base* stitch from previous round
                        base_angle = (2 * np.pi / num_base_stitches_for_current_round) * current_stitch_idx_in_base
                        avg_x_base += current_radius * np.cos(base_angle)
                        avg_z_base += current_radius * np.sin(base_angle)
                        num_consumed_for_avg +=1
                        current_stitch_idx_in_base += 1
                    else: # Ran out of base stitches (pattern error or malformed)
                        print(f"Warning: Not enough base stitches in round {round_data.get('roundNumber', round_idx + 1)} for stitch {stitch_instr['type']}")
                        break
                if num_consumed_for_avg > 0:
                    avg_x_base /= num_consumed_for_avg
                    avg_z_base /= num_consumed_for_avg
                # If num_consumed_for_avg is 0 (e.g. 'ch' stitch not anchored), it will place at origin of current level (0,0)

            # Place the *produced* stitches for the current operation
            # For simplicity, if an inc produces 2, they are placed very close to the avg_x_base, avg_z_base
            # A more complex model would push them out slightly.
            for i in range(props["produces"]):
                # Slight offset for multiple stitches produced from one point (e.g., "inc")
                # This offset is in the direction of the anchor point from the center, crudely.
                # A better way would be perpendicular to the growth direction.
                offset_scale = 1.0
                if props["produces"] > 1 : # For "inc"
                    offset_scale = 1.0 + (i - (props["produces"]-1)/2) * 0.05 # Tiny radial offset

                x = avg_x_base * offset_scale
                z = avg_z_base * offset_scale

                # Convert numpy floats to standard Python floats and round
                coord = [round(float(x), 3), round(float(current_y_level), 3), round(float(z), 3)]
                all_stitch_visual_coordinates.append(coord)
                temp_next_round_base_coords.append(coord)

        previous_round_base_coords = temp_next_round_base_coords
        num_base_stitches_for_current_round = current_round_total_produced_stitches
        current_y_level += current_round_avg_height # Increment Y level for next round

    return all_stitch_visual_coordinates


if __name__ == "__main__":
    print("Testing shape generator (v0.2 format)...")

    # Helper to load pattern from file
    def load_pattern_from_file(filepath):
        # This helper will now simulate the parser's output structure for testing.
        # It reads the JSON string, then uses the actual parse_pattern from the parser module.
        # This makes the test more representative.
        import json # ensure json is imported locally if not at top level of script
        from parser import parse_pattern as actual_parse_pattern # Correctly import the parser

        with open(filepath, 'r') as f:
            pattern_json_string = f.read()
        return actual_parse_pattern(pattern_json_string)

    # Test with basic_sphere_v0.2.json
    print("\n--- Testing with patterns/basic_sphere_v0.2.json ---")
    try:
        sphere_parsed_pattern = load_pattern_from_file("patterns/basic_sphere_v0.2.json")
        coordinates = generate_shape_coordinates(sphere_parsed_pattern)
        print(f"Generated {len(coordinates)} coordinates for the sphere.")
        if coordinates:
            print(f"Sample (first 5): {coordinates[:5]}")
            print(f"Sample (last 5): {coordinates[-5:]}")
            # Check y-levels to see if height is increasing
            y_levels = sorted(list(set(c[1] for c in coordinates)))
            print(f"Distinct Y-levels found: {y_levels}")

    except FileNotFoundError:
        print("Error: Test pattern file patterns/basic_sphere_v0.2.json not found.")
    except Exception as e:
        print(f"Error processing sphere pattern: {e}")
        import traceback
        traceback.print_exc()


    # Test with simple_circle_v0.2.json
    print("\n--- Testing with patterns/simple_circle_v0.2.json ---")
    try:
        circle_parsed_pattern = load_pattern_from_file("patterns/simple_circle_v0.2.json")
        coordinates = generate_shape_coordinates(circle_parsed_pattern)
        print(f"Generated {len(coordinates)} coordinates for the simple circle.")
        if coordinates:
            print(f"Sample (first 5): {coordinates[:5]}")
            y_levels = sorted(list(set(c[1] for c in coordinates)))
            print(f"Distinct Y-levels for circle: {y_levels}")
            # Check if Y-levels increment consistently with stitch height
            expected_y_increment = STITCH_PROPERTIES["sc"]["height"] # sc/inc have same height defined
            is_consistent_growth = True
            if len(y_levels) > 1:
                for i in range(1, len(y_levels)):
                    if abs(y_levels[i] - y_levels[i-1] - expected_y_increment) > 0.01:
                        is_consistent_growth = False
                        break
            if is_consistent_growth:
                print("Circle Y-levels show consistent growth per round as expected.")
            else:
                print("Circle Y-level increments are not consistent, check logic.")


    except FileNotFoundError:
        print("Error: Test pattern file patterns/simple_circle_v0.2.json not found.")
    except Exception as e:
        print(f"Error processing circle pattern: {e}")

    # Test with a simple chain pattern
    print("\n--- Testing with a simple chain pattern ---")
    chain_pattern_direct = {
        "patternName": "Simple Chain Test",
        "rounds": [
            {
                "roundNumber": 1,
                "stitches": [{"type": "ch"}, {"type": "ch"}, {"type": "ch"}]
            }
        ]
    }
    try:
        coordinates = generate_shape_coordinates(chain_pattern_direct)
        print(f"Generated {len(coordinates)} coordinates for the chain.")
        print(f"Coordinates: {coordinates}")
        # Expected: 3 points in a line, y should be 0 for first, then increment for next "round" if any.
        # Current logic for chains in round_idx == 0 places them linearly at current_y_level (0)
        # and then increments current_y_level.
    except Exception as e:
        print(f"Error processing chain pattern: {e}")

    print("\nShape generator tests (v0.2) finished.")
