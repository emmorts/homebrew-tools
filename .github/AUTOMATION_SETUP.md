# Homebrew Formula Automation Setup

This repository is configured to automatically update the dbfsharp formula when a new release is published in the [emmorts/dbfsharp](https://github.com/emmorts/dbfsharp) repository.

## How It Works

1. When a new release is created in `emmorts/dbfsharp`, a workflow triggers a repository dispatch event to this tap repository
2. This repository receives the event and automatically:
   - Downloads all platform release assets (macOS ARM64, macOS x64, Linux x64)
   - Calculates SHA256 checksums for each asset
   - Updates the formula with the new version and checksums
   - Creates a pull request with the changes

## Setup Instructions

### Step 1: Create Personal Access Token (PAT)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Name it something like "Homebrew Tap Auto Update"
4. Select the following scopes:
   - `repo` (Full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't be able to see it again)

### Step 2: Add Secret to dbfsharp Repository

1. Go to `emmorts/dbfsharp` repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `TAP_REPO_TOKEN`
5. Value: Paste the PAT you created in Step 1
6. Click "Add secret"

### Step 3: Create Workflow in dbfsharp Repository

Create the file `.github/workflows/update-homebrew.yml` in the `emmorts/dbfsharp` repository with the following content:

```yaml
name: Update Homebrew Formula

on:
  release:
    types: [published]

jobs:
  trigger-tap-update:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Homebrew tap update
        run: |
          echo "Triggering update for version ${{ github.event.release.tag_name }}"

          curl -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Authorization: token ${{ secrets.TAP_REPO_TOKEN }}" \
            https://api.github.com/repos/emmorts/homebrew-tools/dispatches \
            -d '{
              "event_type": "new_release",
              "client_payload": {
                "version": "${{ github.event.release.tag_name }}"
              }
            }'

          if [ $? -eq 0 ]; then
            echo "✓ Successfully triggered Homebrew formula update"
          else
            echo "✗ Failed to trigger update"
            exit 1
          fi
```

## Manual Testing

You can manually test the automation workflow in this repository:

1. Go to Actions → "Update dbfsharp Formula"
2. Click "Run workflow"
3. Enter a version (e.g., `v0.2.6`)
4. Click "Run workflow"

This will create a test PR to verify everything works correctly.

## How to Use

Once set up, the automation works automatically:

1. Create a new release in `emmorts/dbfsharp` with a version tag (e.g., `v0.2.7`)
2. Ensure the release includes these assets:
   - `dbfsharp-osx-arm64.tar.gz`
   - `dbfsharp-osx-x64.tar.gz`
   - `dbfsharp-linux-x64.tar.gz`
3. Within minutes, a PR will be automatically created in this repository
4. Review and merge the PR

## Troubleshooting

### Workflow doesn't trigger
- Verify the `TAP_REPO_TOKEN` secret is set correctly in the dbfsharp repository
- Check that the token has the `repo` scope
- Ensure the workflow file exists in dbfsharp at `.github/workflows/update-homebrew.yml`

### Downloads fail
- Verify all three platform assets are attached to the release
- Check that asset names match exactly: `dbfsharp-osx-arm64.tar.gz`, `dbfsharp-osx-x64.tar.gz`, `dbfsharp-linux-x64.tar.gz`

### Formula update fails
- Check the workflow logs in the Actions tab
- Verify the formula structure hasn't changed significantly

## Security Notes

- The PAT should only be granted `repo` scope (nothing more)
- The token is stored as an encrypted secret in GitHub
- Consider using a machine user account for the PAT if preferred
- You can revoke the token at any time from GitHub settings
