# Jira Work Reports Guide

This guide covers how to set up and use the Jira work report generation functionality.

## Features

- Automatic connection to Jira API
- Search for tasks where the user participated during a specific month
- Report generation based on Word template
- Send finished report via Telegram bot

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jira Configuration

Add the following parameters to `config.env`:

```env
# Jira Configuration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_USERNAME=your_username@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=PROJECT
REPORT_AUTHOR=Your Name
# Exclude tasks in these statuses (comma-separated, leave empty to include all)
JIRA_EXCLUDED_STATUSES=New,Postponed,Backlog
```

**Note:** The `JIRA_EXCLUDED_STATUSES` parameter allows you to exclude tasks in specific statuses (e.g., "New", "Postponed"). If the parameter is empty or not specified, tasks in all statuses will be included.

#### Getting API Token

1. Log in to Atlassian Cloud
2. Go to Account Settings → Security → API tokens
3. Click "Create API token"
4. Copy the token to the `JIRA_API_TOKEN` parameter

### 3. Template Preparation

Make sure the `resources/report_work_template.docx` file contains:
- Placeholder `<MM>` for month number
- Placeholder `<yyyy>` for year
- Placeholder `(<task>)<title_task>` where tasks will be inserted

## Usage

### Via Telegram Bot

```
/report september
/report august
/report july
```

### Via Command Line

```bash
python jira/jira_report_generator.py september
```

## Supported Month Formats

**English:** january, february, march, april, may, june, july, august, september, october, november, december

**Abbreviations:** jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec

**Russian (transliterated):** janvar, fevral, mart, aprel, maj, ijun, ijul, avgust, sentjabr, oktjabr, nojabr, dekabr

## How It Works

1. **Parse Month** - Determine month number and year
2. **Connect to Jira** - Authenticate via API token
3. **Search Tasks** - JQL queries to find user's tasks:
   - Tasks where user is assignee
   - Tasks created by user
   - Excludes tasks in specified statuses (configurable)
4. **Process Template** - Replace `<MM>` with month number, `<yyyy>` with year
5. **Add Tasks** - Insert task list in format `(<task>)<title_task>`
6. **Generate Report** - Save file as `{author}_work_report_{month}_{year}.docx`

## File Structure

```
├── jira/
│   └── jira_report_generator.py  # Main class for working with Jira
├── bot/telegram_bot.py            # Telegram bot with /report command
├── resources/
│   └── report_work_template.docx  # Report template
├── reports/                       # Folder for saving reports
└── docs/
    └── JIRA_REPORTS_GUIDE.md      # This guide
```

## Testing

Run tests to verify configuration:

```bash
python jira/jira_report_generator.py september
```

## Troubleshooting

### Jira Connection Error

- Check Jira server URL
- Verify API token is correct
- Check internet connection

### Template Not Found

- Ensure `resources/report_work_template.docx` exists
- Check file access permissions

### No Tasks Found

- Verify user has tasks in the specified month
- Check access permissions to Jira projects
- Review excluded statuses configuration

### Encoding Errors in Console

Console encoding errors (e.g., 'charmap' codec) don't affect report generation - they only impact console output display. The generated DOCX files are created correctly.

## Example Commands

```bash
# Generate report for September via Telegram
/report september

# Generate report for August via command line
python jira/jira_report_generator.py august

# Using abbreviated month name
/report sep
```

The finished report will be sent to chat and saved to the `reports/` folder.

## Configuration Examples

### Include All Statuses
```env
JIRA_EXCLUDED_STATUSES=
```

### Exclude New and Backlog Tasks
```env
JIRA_EXCLUDED_STATUSES=New,Backlog,To Do
```

### Exclude Only Postponed
```env
JIRA_EXCLUDED_STATUSES=Postponed
```

## API Reference

### JiraReportGenerator Class

**Methods:**
- `generate_report(month_text)` - Generate report for specified month
- `get_user_tasks_for_month(month_num, year)` - Get user's tasks for month
- `parse_month_year(month_text, current_year)` - Parse month name to number

**Configuration via Environment:**
- `JIRA_SERVER` - Jira server URL
- `JIRA_USERNAME` - User email for authentication
- `JIRA_API_TOKEN` - API token for authentication
- `JIRA_PROJECT_KEY` - Default project key (optional)
- `REPORT_AUTHOR` - Author name for report filename
- `JIRA_EXCLUDED_STATUSES` - Comma-separated list of statuses to exclude
