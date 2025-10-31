# Jira API v3 Migration - Changes Summary

## Issue
The Jira API v2 endpoint (`/rest/api/2/search`) was deprecated and removed by Atlassian in August 2025. Additionally, the v3 endpoint `/rest/api/3/search` is also being deprecated. The application was receiving errors:
```
The requested API has been removed. Please switch to the API /rest/api/3/search/jql
```

**Correct endpoint:** `/rest/api/3/search/jql` ([Atlassian Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-get))

## Root Cause
The `atlassian-python-api` library's `jql()` method was using the deprecated v2 API endpoint, even when `api_version='3'` parameter was passed.

### Additional Issue Found
When attempting to use the library's `resource_url()` method, it was prepending `/rest/api/2/` to the endpoint, resulting in malformed URLs like:
```
rest/api/2/rest/api/3/search  ❌ WRONG
```

Instead of:
```
https://your-domain.atlassian.net/rest/api/3/search/jql  ✅ CORRECT
```

## Solution Implemented

### 1. Added Comprehensive Logging
- Imported `logging` module
- Configured logger at module level
- Added logging statements throughout the codebase for better debugging

### 2. Created New API v3 Method
- Added `_jql_search_v3()` method that directly calls `/rest/api/3/search/jql` endpoint
- Bypasses the library's URL construction by building the full URL manually
- Uses the Jira client's underlying `session.get()` method with direct authentication
- Includes detailed logging at each step with status code validation

### 3. Replaced Old API Calls
- Replaced `self.jira_client.jql()` calls with `self._jql_search_v3()`
- Updated all error handling to use logger

### 4. Enhanced Connection Logging
- Added logging to show the API root URL being used
- Set `cloud=True` for Atlassian Cloud compatibility

## Files Modified
- `jira_integration/jira_report_generator.py`

## Changes Made

### Import Section (Lines 11, 19-20)
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Connection Method (Lines 42-54)
```python
def _connect_to_jira(self):
    """Connect to Jira using API token authentication"""
    try:
        self.jira_client = Jira(
            url=self.jira_server,
            username=self.jira_username,
            password=self.jira_api_token,
            cloud=True
        )
        logger.info(f"Successfully connected to Jira: {self.jira_server}")
        logger.info(f"Jira client API root: {self.jira_client.resource_url('')}")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Jira: {e}")
```

### New API v3 Search Method (Lines 92-131)
```python
def _jql_search_v3(self, jql, limit=200):
    """Execute JQL search using API v3 enhanced search endpoint"""
    logger.info(f"Executing JQL search with API v3: {jql}")
    
    # Build the full API v3 URL manually - using the NEW /search/jql endpoint
    base_url = self.jira_server.rstrip('/')
    full_url = f"{base_url}/rest/api/3/search/jql"
    
    params = {
        'jql': jql,
        'maxResults': limit,
        'fields': ['summary', 'key']
    }
    
    try:
        logger.info(f"API v3 URL: {full_url}")
        logger.info(f"Query params: {params}")
        
        # Use the Jira client's session directly to bypass resource_url()
        response = self.jira_client.session.get(
            full_url,
            params=params,
            auth=(self.jira_username, self.jira_api_token)
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = response.text
            logger.error(f"API returned error: {error_msg}")
            raise Exception(f"API request failed with status {response.status_code}: {error_msg}")
        
        result = response.json()
        logger.info(f"API v3 response: success, issues count: {len(result.get('issues', []))}")
        
        return result
        
    except Exception as e:
        logger.error(f"API v3 request failed: {e}")
        raise
```

### Updated API Call (Line 167)
```python
# OLD: issues_data = self.jira_client.jql(jql, limit=200)
# NEW:
issues_data = self._jql_search_v3(jql, limit=200)
```

## Testing
✅ Module imports successfully
✅ No linting errors
✅ Logging configured properly

## Next Steps

### IMPORTANT: Restart the Bot
The changes will only take effect after restarting the Telegram bot:

```bash
# Stop the current bot process (Ctrl+C)
# Then restart:
python bot/run_bot.py
# or
python start_bot.py
```

### Expected Log Output
After restarting, when running `/report october`, you should see:
```
INFO - Successfully connected to Jira: https://astorsoft.atlassian.net
INFO - Jira client API root: https://astorsoft.atlassian.net/rest/api/2
INFO - Executing JQL search with API v3: assignee = "m.perevertkin@astorsoft.ru" AND updated >= "2025-10-01" AND updated <= "2025-10-31"
INFO - API v3 URL: https://astorsoft.atlassian.net/rest/api/3/search/jql
INFO - Query params: {'jql': '...', 'maxResults': 200, 'fields': ['summary', 'key']}
INFO - Response status code: 200
INFO - API v3 response: success, issues count: X
```

**Key indicators of success:**
- ✅ URL shows proper format: `https://astorsoft.atlassian.net/rest/api/3/search/jql`
- ✅ NOT the old endpoints: `/rest/api/2/search` or `/rest/api/3/search`
- ✅ NOT the malformed: `rest/api/2/rest/api/3/search`
- ✅ Status code: 200
- ✅ No deprecation errors

## Verification
To verify the fix is working:
1. Restart the bot
2. Run `/report october` command
3. Check logs for "API v3" messages
4. Verify no deprecation errors appear
5. Confirm report generates successfully

## References
- [Atlassian API Deprecation Notice](https://developer.atlassian.com/changelog/#CHANGE-2046)
- [Jira REST API v3 Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)

