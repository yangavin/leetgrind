import json
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def get_db():
    with open("db.json", "r") as f:
        return json.load(f)


def save_db(db):
    with open("db.json", "w") as f:
        json.dump(db, f, indent=4)


def check_leetcode_progress():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    users_behind = []

    print(f"Running LeetCode progress check on {today}")

    for username, user_data in db.items():
        # Skip if user doesn't have necessary data
        if not all(key in user_data for key in ["lc_id", "goal", "solved"]):
            print(f"Skipping {username}: Missing required data")
            continue

        # Check if goal is active
        goal_end_date = user_data["goal"][1]
        daily_goal = user_data["goal"][0]

        if today <= goal_end_date:
            print(
                f"Checking {username} with active goal of {daily_goal} problem(s) per day until {goal_end_date}"
            )
            # Goal is active, check LeetCode progress
            lc_id = user_data["lc_id"]
            previous_solved = user_data["solved"]

            try:
                # Make request to LeetCode API
                api_url = f"https://alfa-leetcode-api.onrender.com/{lc_id}/solved"
                print(f"  Fetching data from: {api_url}")
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()

                current_solved = data["solvedProblem"]
                print(
                    f"  Previous solved: {previous_solved}, Current solved: {current_solved}"
                )

                # Update the solved count in the database
                problems_solved_since_last_check = current_solved - previous_solved

                if problems_solved_since_last_check < daily_goal:
                    # User hasn't met their goal
                    users_behind.append(
                        (username, daily_goal, problems_solved_since_last_check)
                    )
                    print(
                        f"  ❌ {username} is behind! Solved {problems_solved_since_last_check}/{daily_goal}"
                    )
                else:
                    print(
                        f"  ✅ {username} is on track! Solved {problems_solved_since_last_check}/{daily_goal}"
                    )

                # Update the solved count in the database
                db[username]["solved"] = current_solved

            except Exception as e:
                print(f"  Error checking progress for {username}: {e}")
        else:
            print(f"Skipping {username}: Goal has expired (end date: {goal_end_date})")

    # Save updated database
    save_db(db)

    if users_behind:
        print("\nUsers who need reminders:")
        for username, goal, actual in users_behind:
            print(
                f"@{username} needs to solve {goal} problems but only solved {actual}"
            )
    else:
        print("\nNo reminders needed - everyone is on track!")

    return users_behind


if __name__ == "__main__":
    check_leetcode_progress()
