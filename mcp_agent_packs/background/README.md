# Background MCP Configuration

This configuration includes basic MCP servers for background tasks and Google
Workspace integration.

## Included Servers

- **mcp-server-time**: Provides time-related functionality
- **google_workspace**: Google Workspace integration with OAuth support,
  https://github.com/taylorwilsdon/google_workspace_mcp

## Required Credentials

Create a `google_workspace.json` file in the credentials folder with:

- `client_id`: Google OAuth client ID
- `client_secret`: Google OAuth client secret
- `user_email`: Your Google email address
