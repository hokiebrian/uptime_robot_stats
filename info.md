## Uptime Robot Single Monitor Statistics

![release_badge](https://img.shields.io/github/v/release/hokiebrian/uptime_robot_stats?style=for-the-badge)
![release_date](https://img.shields.io/github/release-date/hokiebrian/uptime_robot_stats?style=for-the-badge)
[![License](https://img.shields.io/github/license/hokiebrian/uptime_robot_stats?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Installation

This provides statistics for a single Uptime Robot Monitor. You will need an API Key and your Monitor ID from Uptime Robot.

### Install Custom Components

1) Make sure that [Home Assistant Community Store (HACS)](https://github.com/custom-components/hacs) is setup.
2) Go to integrations in HACS
3) click the 3 dots in the top right corner and choose `custom repositories`
4) paste the following into the repository input field `https://github.com/hokiebrian/uptime_robot_stats` and choose category of `Integration`
5) click add and restart HA to let the integration load
6) Go to settings and choose `Devices & Services`
7) Click `Add Integration` and search for `Uptime Robot Monitor Stats`
8) Configure the integration by copying your API Key on the top line and your Monitor ID on the bottom line when prompted
9) The Instance will be named after your monitor ID
