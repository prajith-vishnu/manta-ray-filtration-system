import urllib.request
import json
import ssl  # Handles the Mac security check

def get_ocean_data():
    print("Connecting to public data telemetry...")
    
    # Coordinates directly inside the North Pacific Garbage Patch
    lat = "25.0"
    lon = "-140.0"
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True"
    
    try:
        # Tell Mac to bypass the missing local certificate check
        context = ssl._create_unverified_context()
        
        # Open the URL using our security context
        response = urllib.request.urlopen(url, context=context)
        raw_json = response.read().decode()
        
        # Load the text into a readable Python dictionary
        data = json.loads(raw_json)
        
        # Extract the current weather/marine movement vectors
        current_vector = data["current_weather"]
        velocity = current_vector["windspeed"]
        direction_angle = current_vector["winddirection"]
        
        print("\n--- Telemetry Fetch: SUCCESS ---")
        print(f"Target Zone: North Pacific Gyre ({lat}°N, {lon}°W)")
        print(f"Current Surface Velocity Vector: {velocity} km/h")
        print(f"Current Flow Direction: {direction_angle}°")
        
    except Exception as error:
        print(f"Error fetching data: {error}")

if __name__ == "__main__":
    get_ocean_data()