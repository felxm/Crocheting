from flask import Flask, render_template, request, redirect, url_for
import json # For pretty printing coordinates if needed

# Assuming parser and shape_generator are in the same directory (src.app)
# and Python's import system can find them.
# If running flask from project root: from src.app.parser import parse_pattern
# If running main.py directly for testing: from parser import parse_pattern
try:
    from src.app.parser import parse_pattern
    from src.app.shape_generator import generate_shape_coordinates
except ImportError:
    # This fallback is useful if running main.py directly from src/app for local testing
    # For production/consistent runs, the above should work if PYTHONPATH is set up or it's run as a package.
    print("Attempting fallback imports for parser and shape_generator (e.g. for local main.py execution)")
    from parser import parse_pattern
    from shape_generator import generate_shape_coordinates


app = Flask(__name__, template_folder='../../templates', static_folder='../../static')

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    result_data_str = None

    if request.method == 'POST':
        if 'pattern_file' not in request.files:
            error_message = "No file part in the request."
            return render_template('index.html', error_message=error_message)

        file = request.files['pattern_file']

        if file.filename == '':
            error_message = "No file selected."
            return render_template('index.html', error_message=error_message)

        if file:
            try:
                pattern_string = file.read().decode('utf-8')
                if not pattern_string.strip():
                    raise ValueError("Uploaded file is empty or contains only whitespace.")

                parsed_pattern = parse_pattern(pattern_string)
                coordinates = generate_shape_coordinates(parsed_pattern)
                # Pass the full list of coordinates directly
                result_data = coordinates
                # For the <pre> tag display, we can still show a summary or limited version if needed,
                # but the main thing is that `result_data` passed to template is the full list.
                # Let's create a summary for the <pre> tag.
                if len(coordinates) > 10:
                    display_summary = f"Successfully generated {len(coordinates)} coordinates. First 10 shown below.\n"
                    display_summary += json.dumps(coordinates[:10], indent=2)
                    display_summary += "\n..."
                else:
                    display_summary = json.dumps(coordinates, indent=2)


            except ValueError as e:
                error_message = f"Processing Error: {str(e)}"
                display_summary = None # No summary if error
            except Exception as e:
                error_message = f"An unexpected error occurred: {str(e)}"
                display_summary = None # No summary if error

        # Pass the full coordinates list as 'result_data' for JS
        # Pass the 'display_summary' for the <pre> tag
        return render_template('index.html', error_message=error_message, result_data=result_data, display_summary=display_summary)

    # For GET request
    return render_template('index.html')

if __name__ == '__main__':
    # Note: Relative paths for template/static folders are tricky when running directly.
    # For robust execution, run with `flask run` from the project root or adjust paths.
    # The Flask object instantiation assumes 'templates' and 'static' are three levels up.
    # If running `python src/app/main.py`, these paths might need to be '../../templates' etc.
    # For now, using the paths as defined, expecting `flask run` from root.
    app.run(debug=True, host='0.0.0.0', port=5000)
