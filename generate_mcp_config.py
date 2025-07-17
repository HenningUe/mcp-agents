#!/usr/bin/env python3
"""
MCP Configuration Generator

Generates a secure mcp.json configuration file by merging a template
with credential files, replacing placeholders with actual values.
"""

import json
import os
import re
import subprocess
import sys
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
        self.mcp_agent_packs_dir = Path("mcp_agent_packs")
    
    def discover_mcp_configurations(self) -> list[dict[str, str]]:
        """Discover available MCP template configurations."""
        configurations = []
        
        if not self.mcp_agent_packs_dir.exists():
            print(f"⚠️  MCP agent packs directory not found: {self.mcp_agent_packs_dir}")
            return configurations
        
        # Scan subdirectories for mcp_template.json files
        for subdir in self.mcp_agent_packs_dir.iterdir():
            if subdir.is_dir():
                template_file = subdir / "mcp_template.json"
                if template_file.exists():
                    # Read description from README.md if available
                    readme_file = subdir / "README.md"
                    description = ""
                    if readme_file.exists():
                        try:
                            with open(readme_file, 'r', encoding='utf-8') as f:
                                # Read first line as description
                                first_line = f.readline().strip()
                                if first_line.startswith('# '):
                                    description = first_line[2:]
                        except Exception:
                            pass
                    
                    config_data = {
                        "name": subdir.name,
                        "path": str(template_file),
                        "description": description or "No description available"
                    }
                    prepare_script = subdir / "prepare.py"
                    if prepare_script.exists():
                        config_data["prepare_script"] = str(prepare_script)
                    
                    configurations.append(config_data)
        
        return configurations
    
    def select_mcp_configuration(self) -> dict[str, str]:
        """Let user select an MCP configuration."""
        print("🔍 Discovering available MCP configurations...")
        print()
        
        configurations = self.discover_mcp_configurations()
        
        if not configurations:
            print("❌ No MCP configurations found!")
            print(f"Please ensure mcp_template.json files exist in subdirectories of "
                  f"{self.mcp_agent_packs_dir}")
            raise FileNotFoundError("No MCP configurations available")
        
        print(f"Found {len(configurations)} MCP configuration(s):")
        print()
        
        # Display available configurations
        for i, config in enumerate(configurations, 1):
            print(f"  {i}. {config['name']}")
            print(f"     📄 {config['description']}")
            print()
        
        # Get user selection
        while True:
            try:
                choice = input(f"Select configuration (1-{len(configurations)}): ").strip()
                
                if not choice:
                    print("❌ Please enter a number!")
                    continue
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(configurations):
                    selected_config = configurations[choice_num - 1]
                    print(f"✓ Selected: {selected_config['name']}")
                    return selected_config
                else:
                    print(f"❌ Invalid selection! Please enter a number between 1 and "
                          f"{len(configurations)}")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled by user")
                raise
        
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
        
    def validate_selected_configuration(self) -> bool:
        """Validate that the selected configuration is usable."""
        if not self.template_path.exists():
            print(f"❌ Selected template file not found: {self.template_path}")
            return False
        
        try:
            # Try to load and validate the template
            template = self.load_template()
            errors = self.validate_template(template)
            if errors:
                print("❌ Selected template has validation errors:")
                for error in errors:
                    print(f"   - {error}")
                return False
        except Exception as e:
            print(f"❌ Error loading selected template: {e}")
            return False
        
        return True


def main():
    """Main entry point."""
    print("🔧 MCP Configuration Generator")
    print("=" * 35)
    print()
    
    try:
        # Create generator with default paths
        generator = MCPConfigGenerator(
            credentials_dir="credentials",
            output_path=".vscode/mcp.json"
        )
        
        # Let user select configuration
        selected_config = generator.select_mcp_configuration()
        
        # Update template path
        generator.template_path = Path(selected_config["path"])
        
        # Execute prepare.py if it exists
        if "prepare_script" in selected_config:
            prepare_script_path = selected_config['prepare_script']
            print(f"\n🔧 Running preparation script: {prepare_script_path}")
            try:
                # Use the same python interpreter that runs this script
                result = subprocess.run(
                    [sys.executable, prepare_script_path],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                if result.stdout:
                    print(result.stdout.strip())
                if result.stderr:
                    print(result.stderr.strip())
                print("✅ Preparation script finished successfully.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running preparation script: {prepare_script_path}")
                if e.stdout:
                    print(e.stdout.strip())
                if e.stderr:
                    print(e.stderr.strip())
                return 1
            except FileNotFoundError:
                print(f"❌ Python executable not found: {sys.executable}")
                return 1
        
        # Validate the selected configuration
        if not generator.validate_selected_configuration():
            return 1
        
        print()
        
        # Run the generator
        generator.run()
        
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Make sure you have:")
        print("   - MCP template files in mcp_agent_packs subdirectories")
        print("   - Corresponding credential files in the credentials folder")
        return 1
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
