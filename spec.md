# MCP Configuration Generator Specification

## Overview

Create a Python script that generates a secure `mcp.json` configuration file by
merging a template with credential files.

## Requirements

### 1. Input Files

- **Template**: `mcp_template.json` - Contains MCP server configurations with
  placeholders
- **Credentials Folder**: `credentials/` - Contains JSON files with sensitive
  data
- **Output**: `mcp.json` - Generated configuration file (should be in
  .gitignore)

### 2. Placeholder System

- **Format**: Placeholders are identified by leading and trailing `%` characters
- **Example**: `%GOOGLE_OAUTH_CLIENT_ID%`, `%DATABASE_PASSWORD%`
- **Case Sensitivity**: Placeholders are case-sensitive

### 3. Credential File Mapping

For each server section in `mcp_template.json` under the root `"servers"`
object:

- **Server Name**: `google_workspace` → **Credential File**:
  `credentials/google_workspace.json`
- **Server Name**: `database_server` → **Credential File**:
  `credentials/database_server.json`
- **Server Name**: `email_service` → **Credential File**:
  `credentials/email_service.json`

### 4. Credential File Structure

Each credential file should contain key-value pairs:

```json
{
  "GOOGLE_OAUTH_CLIENT_ID": "your-actual-client-id",
  "GOOGLE_OAUTH_CLIENT_SECRET": "your-actual-client-secret",
  "USER_GOOGLE_EMAIL": "user@gmail.com"
}
```

### 5. Template Example

```json
{
  "servers": {
    "google_workspace": {
      "command": "uvx",
      "args": ["workspace-mcp"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "%GOOGLE_OAUTH_CLIENT_ID%",
        "GOOGLE_OAUTH_CLIENT_SECRET": "%GOOGLE_OAUTH_CLIENT_SECRET%",
        "USER_GOOGLE_EMAIL": "%USER_GOOGLE_EMAIL%"
      },
      "type": "stdio"
    }
  }
}
```

### 6. Script Functionality

- **Read** `mcp_template.json`
- **Scan** for all server sections under `"servers"`
- **Load** corresponding credential files from `credentials/` folder
- **Replace** all placeholders (`%KEY%`) with actual values from credential
  files
- **Generate** `mcp.json` with resolved values
- **Error Handling**:
  - Missing credential files
  - Missing placeholder values
  - Invalid JSON format
  - File permission issues

### 7. Security Considerations

- Credential files should be in `.gitignore`
- Generated `mcp.json` should be in `.gitignore`
- Only `mcp_template.json` should be version controlled
- Script should validate file permissions

### 8. Expected Output Structure

```json
{
  "servers": {
    "google_workspace": {
      "command": "uvx",
      "args": ["workspace-mcp"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "blablabla.apps.googleusercontent.com",
        "GOOGLE_OAUTH_CLIENT_SECRET": "blablabla",
        "USER_GOOGLE_EMAIL": "blablabla"
      },
      "type": "stdio"
    }
  }
}
```

### 9. Usage

```bash
python generate_mcp_config.py
```

### 10. Error Messages

- Clear error messages for missing files
- Validation of JSON syntax
- Warning for unused credential values
- Info about successful placeholder replacements
