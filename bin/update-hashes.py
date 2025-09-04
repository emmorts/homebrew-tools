#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "requests",
#     "click",
# ]
# ///

"""
Updates SHA256 hashes in Homebrew Formula files by fetching the latest release from GitHub.

This script parses a Homebrew Formula file to extract repository and version information,
fetches the corresponding release from GitHub, downloads the artifacts, calculates their
SHA256 hashes, and updates the Formula file.
"""

import re
import sys
import hashlib
import tempfile
import os
from pathlib import Path
from urllib.parse import urlparse
import requests
import click


def parse_formula(formula_path: Path) -> dict:
    """Parse a Homebrew Formula file to extract repository and version info."""
    if not formula_path.exists():
        raise FileNotFoundError(f"Formula file not found: {formula_path}")
    
    content = formula_path.read_text(encoding='utf-8')
    
    # Extract homepage (GitHub repository)
    homepage_match = re.search(r'homepage\s+"([^"]+)"', content)
    if not homepage_match:
        raise ValueError("Could not find homepage in Formula file")
    
    homepage = homepage_match.group(1)
    
    # Extract version
    version_match = re.search(r'version\s+"([^"]+)"', content)
    if not version_match:
        raise ValueError("Could not find version in Formula file")
    
    version = version_match.group(1)
    
    # Extract existing URLs to understand the pattern
    url_matches = re.findall(r'url\s+"([^"]+)"', content)
    
    return {
        'homepage': homepage,
        'version': version,
        'existing_urls': url_matches,
        'content': content
    }


def extract_repo_info(homepage: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    # Handle both https://github.com/owner/repo and github.com/owner/repo
    pattern = r'github\.com[/:](.*?)/(.*?)(?:\.git)?/?$'
    match = re.search(pattern, homepage)
    
    if not match:
        raise ValueError(f"Invalid GitHub repository URL: {homepage}")
    
    return match.group(1), match.group(2)


def get_release_info(owner: str, repo: str, version: str = None) -> dict:
    """Fetch release information from GitHub API."""
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    if version:
        # Try with 'v' prefix first, then without
        for tag in [f"v{version}", version]:
            url = f"{base_url}/releases/tags/{tag}"
            response = requests.get(url, headers={
                "User-Agent": "Homebrew-Hash-Updater",
                "Accept": "application/vnd.github.v3+json"
            })
            if response.status_code == 200:
                return response.json()
    else:
        url = f"{base_url}/releases/latest"
        response = requests.get(url, headers={
            "User-Agent": "Homebrew-Hash-Updater",
            "Accept": "application/vnd.github.v3+json"
        })
    
    if response.status_code == 404:
        raise ValueError(f"Repository {owner}/{repo} or release not found")
    elif response.status_code != 200:
        raise ValueError(f"GitHub API error: {response.status_code} - {response.text}")
    
    return response.json()


def filter_relevant_assets(assets: list, existing_urls: list) -> list:
    """Filter assets based on patterns from existing URLs in the formula."""
    if not existing_urls:
        # Default patterns for common cross-platform tools
        patterns = [
            r".*osx.*arm64.*",
            r".*osx.*x64.*",
            r".*macos.*arm64.*", 
            r".*macos.*x64.*",
            r".*darwin.*arm64.*",
            r".*darwin.*x64.*",
            r".*linux.*x64.*",
            r".*linux.*arm64.*"
        ]
    else:
        # Extract patterns from existing URLs
        patterns = []
        for url in existing_urls:
            filename = os.path.basename(url)
            # Create a pattern based on the filename structure
            if "osx" in filename or "macos" in filename or "darwin" in filename:
                if "arm64" in filename:
                    patterns.append(r".*(?:osx|macos|darwin).*arm64.*")
                elif "x64" in filename:
                    patterns.append(r".*(?:osx|macos|darwin).*x64.*")
            elif "linux" in filename:
                if "arm64" in filename:
                    patterns.append(r".*linux.*arm64.*")
                elif "x64" in filename:
                    patterns.append(r".*linux.*x64.*")
    
    relevant_assets = []
    for asset in assets:
        asset_name = asset['name'].lower()
        for pattern in patterns:
            if re.match(pattern, asset_name, re.IGNORECASE):
                relevant_assets.append(asset)
                break
    
    return relevant_assets


def download_and_hash(url: str, temp_dir: Path) -> str:
    """Download a file and calculate its SHA256 hash."""
    filename = os.path.basename(urlparse(url).path)
    filepath = temp_dir / filename
    
    click.echo(f"  Downloading {filename}...", nl=False)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    sha256_hash = hashlib.sha256()
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            sha256_hash.update(chunk)
    
    click.echo(" Done", color=True)
    hash_value = sha256_hash.hexdigest()
    click.echo(f"  SHA256: {hash_value}")
    return hash_value


def determine_platform_arch(asset_name: str) -> tuple[str, str]:
    """Determine platform and architecture from asset name."""
    name_lower = asset_name.lower()
    
    # Platform detection
    if any(p in name_lower for p in ['osx', 'macos', 'darwin']):
        platform = 'macos'
    elif 'linux' in name_lower:
        platform = 'linux'
    elif any(p in name_lower for p in ['win', 'windows']):
        platform = 'windows'
    else:
        platform = 'unknown'
    
    # Architecture detection
    if 'arm64' in name_lower:
        arch = 'arm64'
    elif 'x64' in name_lower or 'x86_64' in name_lower or 'amd64' in name_lower:
        arch = 'x64'
    else:
        arch = 'unknown'
    
    return platform, arch


def update_formula_content(content: str, version: str, asset_updates: dict) -> str:
    """Update the Formula content with new version and hashes."""
    updated_content = content
    
    # Update version if it has changed
    version_pattern = r'(version\s+")[^"]*(")'
    if re.search(version_pattern, updated_content):
        updated_content = re.sub(version_pattern, f'\\g<1>{version}\\g<2>', updated_content)
        click.echo(f"  Updated version to: {version}")
    
    # Update URLs and SHA256 hashes
    for asset_info in asset_updates.values():
        platform = asset_info['platform']
        arch = asset_info['arch']
        url = asset_info['url']
        hash_value = asset_info['hash']
        
        # Build patterns to match the appropriate section in the formula
        if platform == 'macos':
            if arch == 'arm64':
                url_pattern = r'(on_macos\s+do.*?on_arm\s+do.*?url\s+")[^"]*(")'
                hash_pattern = r'(on_macos\s+do.*?on_arm\s+do.*?url\s+"[^"]*"\s+sha256\s+")[^"]*(")'
            elif arch == 'x64':
                url_pattern = r'(on_macos\s+do.*?on_intel\s+do.*?url\s+")[^"]*(")'
                hash_pattern = r'(on_macos\s+do.*?on_intel\s+do.*?url\s+"[^"]*"\s+sha256\s+")[^"]*(")'
            else:
                continue
        elif platform == 'linux':
            if arch == 'x64':
                url_pattern = r'(on_linux\s+do.*?on_intel\s+do.*?url\s+")[^"]*(")'
                hash_pattern = r'(on_linux\s+do.*?on_intel\s+do.*?url\s+"[^"]*"\s+sha256\s+")[^"]*(")'
            else:
                continue
        else:
            continue
        
        # Apply updates using DOTALL flag to handle multiline matching
        flags = re.DOTALL | re.MULTILINE
        if re.search(url_pattern, updated_content, flags):
            updated_content = re.sub(url_pattern, f'\\g<1>{url}\\g<2>', updated_content, flags=flags)
            updated_content = re.sub(hash_pattern, f'\\g<1>{hash_value}\\g<2>', updated_content, flags=flags)
            click.echo(f"  Updated {platform}-{arch}: URL and SHA256 for {os.path.basename(url)}")
        else:
            click.echo(f"  Warning: Could not find pattern to update {platform}-{arch}", color='yellow')
    
    return updated_content


@click.command()
@click.argument('formula_path', type=click.Path(exists=True, path_type=Path))
@click.option('--version', help='Specific version to fetch (if not provided, uses version from formula or latest)')
@click.option('--dry-run', is_flag=True, help='Show what would be updated without making changes')
def main(formula_path: Path, version: str, dry_run: bool):
    """Update SHA256 hashes in a Homebrew Formula file by fetching the latest release."""
    
    try:
        # Parse the formula file
        click.echo(f"Parsing Formula file: {formula_path}")
        formula_info = parse_formula(formula_path)
        
        homepage = formula_info['homepage']
        current_version = formula_info['version']
        existing_urls = formula_info['existing_urls']
        
        click.echo(f"Repository: {homepage}")
        click.echo(f"Current version: {current_version}")
        
        # Extract repository information
        owner, repo = extract_repo_info(homepage)
        click.echo(f"GitHub repo: {owner}/{repo}")
        
        # Use provided version or fall back to formula version
        target_version = version or current_version
        
        # Get release information
        click.echo(f"Fetching release information for version: {target_version}")
        release_info = get_release_info(owner, repo, target_version)
        
        release_version = release_info['tag_name'].lstrip('v')
        click.echo(f"Found release: {release_info['tag_name']} ({release_version})")
        click.echo(f"Published: {release_info['published_at']}")
        
        # Filter relevant assets
        relevant_assets = filter_relevant_assets(release_info['assets'], existing_urls)
        
        if not relevant_assets:
            click.echo("No relevant assets found!", color='red')
            click.echo("Available assets:")
            for asset in release_info['assets']:
                click.echo(f"  - {asset['name']}")
            return 1
        
        click.echo(f"Found {len(relevant_assets)} relevant assets:")
        for asset in relevant_assets:
            click.echo(f"  - {asset['name']}")
        
        if dry_run:
            click.echo("\nDry run mode - no changes will be made")
            return 0
        
        # Download assets and calculate hashes
        asset_updates = {}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            click.echo(f"\nUsing temporary directory: {temp_path}")
            
            for asset in relevant_assets:
                click.echo(f"\nProcessing: {asset['name']}")
                
                try:
                    hash_value = download_and_hash(asset['browser_download_url'], temp_path)
                    platform, arch = determine_platform_arch(asset['name'])
                    
                    asset_updates[asset['name']] = {
                        'url': asset['browser_download_url'],
                        'hash': hash_value,
                        'platform': platform,
                        'arch': arch
                    }
                    
                except Exception as e:
                    click.echo(f"  Error processing {asset['name']}: {e}", color='red')
                    continue
        
        # Update the formula file
        if asset_updates:
            click.echo(f"\nUpdating Formula file...")
            updated_content = update_formula_content(
                formula_info['content'], 
                release_version, 
                asset_updates
            )
            
            formula_path.write_text(updated_content, encoding='utf-8')
            click.echo("Formula file updated successfully!", color='green')
            
            # Show summary
            click.echo(f"\nSummary:")
            click.echo(f"  Version: {release_version}")
            click.echo(f"  Assets updated:")
            for asset_name, info in asset_updates.items():
                click.echo(f"    {asset_name}: {info['hash']}")
        else:
            click.echo("No assets were processed successfully.", color='red')
            return 1
            
    except Exception as e:
        click.echo(f"Error: {e}", color='red')
        return 1
    
    click.echo("\nDone!", color='green')
    return 0


if __name__ == '__main__':
    sys.exit(main())
