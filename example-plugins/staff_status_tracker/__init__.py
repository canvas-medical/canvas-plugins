"""Staff Status Tracker Plugin."""

# This plugin tracks staff status changes by:
# 1. Running a weekly cron job to collect all staff status data
# 2. Listening for staff activation/deactivation events to track changes
# 3. Storing CSV data in cache for 7 days