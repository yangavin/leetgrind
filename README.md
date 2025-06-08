# LeetCode Progress Tracker

A Discord bot that tracks LeetCode progress and sends daily reminders to users who haven't met their goals. The bot also displays a weekly leaderboard every Monday.

## 🚀 Features

### Daily Progress Tracking

- Automatically fetches LeetCode statistics for all users
- Calculates points based on problem difficulty:
  - Easy: 1 point
  - Medium: 2 points
  - Hard: 3 points
- Tags users in Discord who haven't met their daily goals
- Updates user progress in the database

### Weekly Leaderboard

- Every Monday, displays a leaderboard ranked by weekly points
- Resets weekly points after displaying the leaderboard
- Motivational messages for users with different performance levels

### Goal Management

- Users can set daily point goals with end dates
- Automatically clears expired goals
- Flexible goal system supporting different targets per user

## 📊 Database Schema

The system uses a JSON database (`db.json`) with this structure:

```json
{
  "username": {
    "lc_id": "leetcode_username",
    "goal": [daily_points, "end_date"],
    "easySolved": 10,
    "mediumSolved": 5,
    "hardSolved": 2,
    "points": 19,
    "weekly_points": 5
  }
}
```

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Discord bot token
- LeetCode API access

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd leetgrind
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   CHANNEL_ID=your_discord_channel_id
   LEETCODE_API_URL=your_leetcode_api_url
   ```

## 🎯 Usage

### Run the Progress Checker

```bash
python check_leetcode.py
```

### Test Mode (Print Only)

To test without sending Discord messages or updating the database:

```bash
python check_leetcode.py --print
```

### Discord Bot Commands

Start the Discord bot with slash commands:

```bash
python main.py
```

### Scheduled Execution

Set up a cron job to run the progress checker daily at 12 AM:

```bash
0 0 * * * /path/to/python /path/to/check_leetcode.py
```

## 📁 Repository Structure

```
├── models.py                 # Data models and type definitions
├── database.py               # Database operations
├── leetcode_api.py          # LeetCode API interactions
├── points_calculator.py     # Points calculation logic
├── goal_checker.py          # Goal validation and checking
├── leaderboard.py           # Weekly leaderboard functionality
├── discord_bot.py           # Discord operations
├── leetcode_service.py      # Main service orchestrator
├── check_leetcode.py        # Progress checker entry point
├── main.py                  # Discord bot with slash commands
├── test_*.py                # Test files
├── requirements.txt         # Python dependencies
├── db.json                  # User data database
└── .env                     # Environment configuration
```

## 🔧 Configuration

### Environment Variables

- `DISCORD_TOKEN`: Your Discord bot token
- `CHANNEL_ID`: Discord channel ID for progress messages
- `LEETCODE_API_URL`: LeetCode API endpoint

### Customization

- **Point Values**: Modify `PROBLEM_SCALE` in `models.py`
- **Messages**: Update templates in `discord_bot.py` and `leaderboard.py`
- **Database Location**: Configure path in `DatabaseManager`

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Run all tests
pytest -v

# Run specific test modules
pytest test_models.py -v
pytest test_database.py -v
```

## 🚨 Error Handling

The system gracefully handles:

- LeetCode API failures
- Invalid database entries
- Missing environment variables
- Discord connection issues
- Expired goals (automatically cleaned up)

## 🤝 Contributing

1. Follow the modular architecture
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting changes
