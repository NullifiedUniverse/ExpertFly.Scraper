import random
import time
import sys
import math # Import math for ceiling function if needed later, but not strictly for pairing

def simple_animation(duration=1.5, message="Processing"):
    """Displays a simple spinning cursor animation."""
    chars = "|/-\\"
    start_time = time.time()
    idx = 0
    while time.time() - start_time < duration:
        # Use \r to return cursor to the beginning of the line
        sys.stdout.write(f"\r{message}... {chars[idx % len(chars)]}")
        sys.stdout.flush() # Force output to display
        time.sleep(0.01)
        idx += 1
    # Clear the animation line
    sys.stdout.write("\r" + " " * (len(message) + 5) + "\r")
    sys.stdout.flush()

def get_positive_integer_input(prompt):
    """Gets positive integer input from the user."""
    while True:
        try:
            value_str = input(prompt).strip()
            value = int(value_str)
            if value > 0:
                return value
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def generate_pairings(num_teams):
    """Generates and displays random pairings for a given number of teams."""
    if num_teams < 2:
        print("You need at least 2 teams to form pairings.")
        return

    print(f"\nGenerating pairings for {num_teams} teams.")
    # Create a list of generic team names
    teams = [f"Team {i+1}" for i in range(num_teams)]

    # --- Animation ---
    simple_animation(message="Shuffling Teams")

    # --- Random Pairing Logic ---
    random.shuffle(teams)

    pairings = []
    bye_team = None

    # Handle odd number of teams: the last shuffled team gets a bye
    if num_teams % 2 != 0:
        bye_team = teams.pop() # Remove the last team for the bye

    # Create pairs from the remaining (or all if even) teams
    # Iterate through the list taking 2 teams at a time
    for i in range(0, len(teams), 2):
        # Ensure there's a second team to pair with (safety check)
        if i + 1 < len(teams):
            pairings.append((teams[i], teams[i+1]))

    # --- Display Results ---
    print("\n--- Tournament Matchups ---")
    if not pairings and not bye_team:
         print("No pairings could be generated.") # Should not happen if num_teams >= 2
         return

    if pairings:
        match_num = 1
        # Calculate padding for alignment based on longest team name
        # Assumes team names like "Team X", "Team XX", etc.
        max_len = len(f"Team {num_teams}")
        for team1, team2 in pairings:
            # Use f-string formatting for alignment
            print(f"Match {match_num}: {team1:<{max_len}}  vs  {team2:<{max_len}}")
            match_num += 1
            time.sleep(0.01) # Small delay for dramatic effect

    if bye_team:
        print(f"\n{bye_team} receives a BYE for this round.")

    print("---------------------------\n")


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Basketball Tournament Pairings ---")
    number_of_teams = get_positive_integer_input("Enter the total number of participating teams: ")
    generate_pairings(number_of_teams)
    print("Pairing complete. Good luck!")
    time.sleep(100000)
