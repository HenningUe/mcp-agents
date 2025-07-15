#!/usr/bin/env python3
"""
MCP Configuration Generator

Generates a secure mcp.json configuration file by merging a template
with credential files, replacing placeholders with actual values.
"""

import json
import os
import re
import typing as tp
from pathlib import Path


class MCPConfigGenerator:
    """Generates MCP configuration by merging template with credentials."""
    
    def __init__(self, template_path: str = "mcp_template.json",
                 credentials_dir: str = "credentials",
                 output_path: str = "mcp.json"):
        self.template_path = Path(template_path)
        self.credentials_dir = Path(credentials_dir)
        self.output_path = Path(output_path)
        self.placeholder_pattern = re.compile(r'%([a-zA-Z_][a-zA-Z0-9_]*)%')
        
    def load_template(self) -> dict[str, tp.Any]:
        """Load the MCP template file."""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            print(f"✓ Loaded template from {self.template_path}")
            return template
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Template file not found: {self.template_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file: {e}")

    def load_credentials(self, server_name: str, placeholder_list: set[str]) -> dict[str, str]:
        """Load credentials for a specific server."""
        credentials_file = self.credentials_dir / f"{server_name}.json"
        
        if not credentials_file.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_file}")
        
        try:
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credt_file_content = json.load(f)
            print(f"✓ Loaded credentials for {server_name}")
            placeholder_list = set(x.strip('%') for x in placeholder_list)
            credentials_condensed = self.find_secret_values_from_credentials_recursively(
                credt_file_content, placeholder_list)
            return credentials_condensed
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in credentials file {credentials_file}: {e}")

    def find_secret_values_from_credentials_recursively(
        self, obj: tp.Any, keys: set[str],
    ) -> dict[str, str]:
        """Recursively find all credentials in a JSON object."""
        credentials = {}

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    if key in keys:
                        credentials[key] = value
                else:
                    credentials.update(
                        self.find_secret_values_from_credentials_recursively(value, keys))
        return credentials
    
    def find_placeholders(self, obj: tp.Any) -> set[str]:
        """Recursively find all placeholders in a JSON object."""
        placeholders = set()
        
        if isinstance(obj, dict):
            for value in obj.values():
                placeholders.update(self.find_placeholders(value))
        elif isinstance(obj, list):
            for item in obj:
                placeholders.update(self.find_placeholders(item))
        elif isinstance(obj, str):
            matches = self.placeholder_pattern.findall(obj)
            placeholders.update(matches)
        
        return placeholders

    def replace_placeholders(self, obj: tp.Any,
                             credentials: dict[str, str]) -> tp.Any:
        """Recursively replace placeholders in a JSON object."""
        if isinstance(obj, dict):
            return {key: self.replace_placeholders(value, credentials)
                    for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_placeholders(item, credentials)
                    for item in obj]
        elif isinstance(obj, str):
            def replace_func(match):
                placeholder = match.group(1)
                if placeholder in credentials:
                    return credentials[placeholder]
                else:
                    raise ValueError(
                        f"Missing credential for placeholder: "
                        f"%{placeholder}%")
            return self.placeholder_pattern.sub(replace_func, obj)
        else:
            return obj
    
    def validate_template(self, template: dict[str, tp.Any]) -> list[str]:
        """Validate the template structure."""
        errors = []
        
        if not isinstance(template, dict):
            errors.append("Template must be a JSON object")
            return errors
        
        if "servers" not in template:
            errors.append("Template must contain a 'servers' section")
            return errors
        
        servers = template["servers"]
        if not isinstance(servers, dict):
            errors.append("'servers' section must be a JSON object")
            return errors
        
        if not servers:
            errors.append("'servers' section cannot be empty")
        
        return errors
    
    def check_file_permissions(self):
        """Check if we have the necessary file permissions."""
        # Check if credentials directory exists
        if not self.credentials_dir.exists():
            raise FileNotFoundError(
                f"Credentials directory not found: {self.credentials_dir}")
        
        # Check if credentials directory is readable
        if not os.access(self.credentials_dir, os.R_OK):
            raise PermissionError(
                f"Cannot read credentials directory: {self.credentials_dir}")
        
        # Check if we can write to output directory
        output_dir = self.output_path.parent
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(
                f"Cannot write to output directory: {output_dir}")
    
    def generate_config(self) -> dict[str, tp.Any]:
        """Generate the MCP configuration."""
        print("🚀 Starting MCP configuration generation...")
        
        # Check file permissions
        self.check_file_permissions()
        
        # Load template
        template = self.load_template()
        
        # Validate template
        errors = self.validate_template(template)
        if errors:
            error_msg = ("Template validation failed:\n" +
                         "\n".join(f"  - {error}" for error in errors))
            raise ValueError(error_msg)
        
        # Process each server
        servers = template["servers"]
        processed_servers = {}
        
        for server_name, server_config in servers.items():
            print(f"\n📋 Processing server: {server_name}")
            
            # Find placeholders in this server's configuration
            placeholders = self.find_placeholders(server_config)
            
            if not placeholders:
                print(f"  ℹ️  No placeholders found for {server_name}")
                processed_servers[server_name] = server_config
                continue
            
            placeholder_list = ', '.join(f'%{p}%' for p in placeholders)
            print(f"  🔍 Found placeholders: {placeholder_list}")
            
            # Load credentials for this server
            try:
                credentials = self.load_credentials(server_name, placeholders)
            except FileNotFoundError as e:
                print(f"  ❌ {e}")
                raise
            
            # Check if all placeholders have corresponding credentials
            missing_credentials = placeholders - set(credentials.keys())
            if missing_credentials:
                missing_list = ', '.join(f'%{p}%' for p in missing_credentials)
                raise ValueError(
                    f"Missing credentials for {server_name}: {missing_list}")
            
            # Check for unused credentials
            unused_credentials = set(credentials.keys()) - placeholders
            if unused_credentials:
                unused_list = ', '.join(unused_credentials)
                print(f"  ⚠️  Unused credentials in {server_name}: "
                      f"{unused_list}")
            
            # Replace placeholders
            processed_config = self.replace_placeholders(
                server_config, credentials)
            processed_servers[server_name] = processed_config
            
            print(f"  ✅ Successfully processed {len(placeholders)} "
                  f"placeholders")
        
        # Create final configuration
        final_config = template.copy()
        final_config["servers"] = processed_servers
        
        return final_config
    
    def save_config(self, config: dict[str, tp.Any]):
        """Save the generated configuration to file."""
        self.output_path.unlink(missing_ok=True)
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Configuration saved to {self.output_path}")
        except Exception as e:
            raise IOError(f"Failed to save configuration: {e}")

    def run(self):
        """Run the configuration generation process."""
        config = self.generate_config()
        self.save_config(config)
        print("\n🎉 MCP configuration generated successfully!")
        print(f"📄 Output file: {self.output_path}")
        print("\n💡 Remember to:")
        print("   - Add mcp.json to .gitignore")
        print("   - Keep credentials/ folder secure")
        print("   - Only commit mcp_template.json to version control")


def main():
    """Main entry point."""
    print("🔧 MCP Configuration Generator")
    print("=" * 35)
    
    # You can customize these paths if needed
    generator = MCPConfigGenerator(
        template_path=".vscode/mcp_template.json",
        credentials_dir="credentials",
        output_path=".vscode/mcp.json"
    )
    
    generator.run()


if __name__ == "__main__":
    main()
