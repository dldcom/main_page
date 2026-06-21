import os
import sys
import argparse
import subprocess

try:
    import requests
except ImportError:
    print("The 'requests' library is not installed. Please install it by running: pip install requests")
    sys.exit(1)

# Load .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val.strip("'\"")

GITHUB_USERNAME = "dldcom"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CLOUDFLARE_TOKEN = os.environ.get("CLOUDFLARE_TOKEN")

if not GITHUB_TOKEN or not CLOUDFLARE_TOKEN:
    print("Error: GITHUB_TOKEN or CLOUDFLARE_TOKEN is missing. Please set them in the .env file.")
    sys.exit(1)

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e.stderr}")
        sys.exit(1)

def create_github_repo(repo_name, is_private=False):
    print(f"Creating GitHub repository: {repo_name}...")
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": is_private
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Successfully created GitHub repository: {repo_name}")
        return response.json()['clone_url']
    elif response.status_code == 422: # Unprocessable Entity
        print(f"Repository {repo_name} might already exist. Proceeding...")
        return f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"
    else:
        print(f"Failed to create GitHub repository. Status code: {response.status_code}\n{response.text}")
        sys.exit(1)

def push_to_github(repo_dir, repo_name, domain):
    print("Initializing Git, committing, and pushing...")
    
    # Create CNAME file for GitHub Pages custom domain
    cname_path = os.path.join(repo_dir, "CNAME")
    with open(cname_path, "w") as f:
        f.write(domain)
    
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        run_command("git init", cwd=repo_dir)
        run_command("git branch -M main", cwd=repo_dir)
    
    run_command("git add .", cwd=repo_dir)
    
    try:
        subprocess.run('git commit -m "Add code and CNAME for custom domain"', cwd=repo_dir, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Nothing to commit or commit failed. Moving on...")
    
    remote_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{repo_name}.git"
    
    try:
        remotes = run_command("git remote", cwd=repo_dir)
        if "origin" not in remotes:
            run_command(f"git remote add origin {remote_url}", cwd=repo_dir)
        else:
            run_command(f"git remote set-url origin {remote_url}", cwd=repo_dir)
    except Exception:
        run_command(f"git remote add origin {remote_url}", cwd=repo_dir)
        
    run_command("git push -u origin main", cwd=repo_dir)
    print("Code successfully pushed to GitHub.")

def configure_github_pages(repo_name):
    # Enable GitHub Pages to build from 'main' branch root
    print("Configuring GitHub Pages...")
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [201, 204]:
        print("GitHub Pages successfully enabled.")
    elif response.status_code == 409: # Already exists
        print("GitHub Pages is already enabled for this repository.")
    else:
        print(f"Note: GitHub Pages API returned {response.status_code}. It might already be enabled or configuring automatically.")

def get_cloudflare_zone_id(base_domain):
    print(f"Fetching Cloudflare Zone ID for {base_domain}...")
    url = f"https://api.cloudflare.com/client/v4/zones?name={base_domain}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        zones = response.json().get('result', [])
        if not zones:
            print(f"Error: No zone found for domain {base_domain}.")
            sys.exit(1)
        return zones[0]['id']
    else:
        print(f"Failed to fetch zone info. Status code: {response.status_code}\n{response.text}")
        sys.exit(1)

def create_cloudflare_dns_record(zone_id, subdomain):
    print(f"Creating Cloudflare DNS CNAME record for {subdomain}...")
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # We point the CNAME to GitHub Pages default domain: dldcom.github.io
    data = {
        "type": "CNAME",
        "name": subdomain,
        "content": f"{GITHUB_USERNAME}.github.io",
        "proxied": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"Successfully created DNS record. {subdomain} -> {GITHUB_USERNAME}.github.io")
    else:
        # Check if record already exists (Code 81053)
        res_json = response.json()
        errors = res_json.get('errors', [])
        if any(err.get('code') == 81053 for err in errors):
            print(f"DNS record for {subdomain} already exists.")
        else:
            print(f"Failed to create DNS record. Status code: {response.status_code}\n{response.text}")

def main():
    parser = argparse.ArgumentParser(description="Automate GitHub push, Pages setup, and Cloudflare DNS mapping.")
    parser.add_argument("--project-name", required=True, help="Name of the project (used for repo)")
    parser.add_argument("--dir", required=True, help="Local directory of the code")
    parser.add_argument("--domain", required=True, help="Custom subdomain (e.g., test.dldcom.xyz)")
    
    args = parser.parse_args()
    
    repo_dir = os.path.abspath(args.dir)
    if not os.path.exists(repo_dir):
        print(f"Error: Directory {repo_dir} does not exist.")
        sys.exit(1)
        
    # Extract base domain from subdomain (e.g., test.dldcom.xyz -> dldcom.xyz)
    parts = args.domain.split('.')
    if len(parts) >= 2:
        base_domain = f"{parts[-2]}.{parts[-1]}"
    else:
        base_domain = args.domain
        
    print(f"--- Starting deployment automation for '{args.project_name}' ---")
    
    # 1. Create GitHub Repo
    create_github_repo(args.project_name)
    
    # 2. Push to GitHub (also adds CNAME file)
    push_to_github(repo_dir, args.project_name, args.domain)
    
    # 3. Configure GitHub Pages
    configure_github_pages(args.project_name)
    
    # 4. Get Cloudflare Zone ID for the base domain
    zone_id = get_cloudflare_zone_id(base_domain)
    
    # 5. Create DNS CNAME Record pointing to GitHub Pages
    create_cloudflare_dns_record(zone_id, args.domain)
    
    print("\n--- Automation Completed! ---")
    print(f"Code is pushed to: https://github.com/{GITHUB_USERNAME}/{args.project_name}")
    print(f"DNS setup complete. GitHub Pages site will be available at: https://{args.domain}")
    print("(Note: DNS propagation and GitHub Pages build may take a minute or two)")

if __name__ == "__main__":
    main()
