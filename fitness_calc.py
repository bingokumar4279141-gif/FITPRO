"""
Fitness Calculation Module
Calculates stride length and calories burned based on user data and established fitness formulas.
"""


def calculate_stride_length(height_cm, gender="male"):
    """
    Calculate stride length based on height and gender.
    
    Args:
        height_cm (float): User's height in centimeters
        gender (str): User's gender ("male", "female", or other)
    
    Returns:
        float: Stride length in centimeters
    
    Formula:
        Male: Stride Length (cm) = Height (cm) × 0.415
        Female: Stride Length (cm) = Height (cm) × 0.413
        Other: Stride Length (cm) = Height (cm) × 0.414
    """
    gender_lower = gender.lower().strip()
    
    if gender_lower == "male":
        stride_multiplier = 0.415
    elif gender_lower == "female":
        stride_multiplier = 0.413
    else:
        stride_multiplier = 0.414
    
    stride_length_cm = height_cm * stride_multiplier
    return stride_length_cm


def calculate_calories_burned(steps, weight_kg, stride_length_cm):
    """
    Calculate total calories burned based on steps, weight, and stride length.
    
    Args:
        steps (int): Number of steps taken
        weight_kg (float): User's weight in kilograms
        stride_length_cm (float): Stride length in centimeters
    
    Returns:
        float: Total calories burned (kcal)
    
    Formula:
        Total Distance (km) = (Steps × Stride Length (cm)) / 100,000
        Calories Burned = 0.5 × Weight (kg) × Total Distance (km)
    """
    # Convert steps and stride length to kilometers
    total_distance_km = (steps * stride_length_cm) / 100000
    
    # Calculate calories burned
    calories_burned = 0.5 * weight_kg * total_distance_km
    
    return calories_burned


def main():
    """Demonstrate stride length and calorie calculation with example data."""
    # Example data
    height_cm = 175
    gender = "male"
    weight_kg = 70
    steps = 10000
    
    # Calculate stride length
    stride_length = calculate_stride_length(height_cm, gender)
    print(f"Height: {height_cm} cm")
    print(f"Gender: {gender}")
    print(f"Calculated Stride Length: {stride_length:.2f} cm ({stride_length/100:.2f} m)\n")
    
    # Calculate distance
    distance_km = (steps * stride_length) / 100000
    print(f"Steps: {steps}")
    print(f"Total Distance: {distance_km:.2f} km\n")
    
    # Calculate calories burned
    calories = calculate_calories_burned(steps, weight_kg, stride_length)
    print(f"Weight: {weight_kg} kg")
    print(f"Calories Burned: {calories:.2f} kcal\n")
    
    print("=" * 50)
    print(f"Summary: {steps} steps with {stride_length:.2f}cm stride")
    print(f"Distance: {distance_km:.2f} km | Calories: {calories:.2f} kcal")


if __name__ == "__main__":
    main()
