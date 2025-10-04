from datetime import timedelta

DOMAIN = "uptime_robot_stats"
BASE_URL = "https://api.uptimerobot.com/v2/getMonitors"
BASE_API_URL = "https://api.uptimerobot.com/v2"

CONF_API_KEY = "api_key"
CONF_MONITOR_ID = "monitor_id"

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=1)
RESPONSE_TIMEOUT = 8
LOOKBACK_PERIOD = 1800
