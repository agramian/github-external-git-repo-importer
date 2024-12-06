import os
import subprocess
import sys
import re


def run_command(command, error_message, dry_run=False):
    """Runs a shell command, with optional dry run support."""
    if dry_run:
        print(f"[DRY RUN] Command: {command}")
        return
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}\nCommand: {e.cmd}\n")
        sys.exit(1)


def parse_github_url(url):
    """
    Parses a GitHub or GitHub Enterprise URL to extract owner and repo name.

    :param url: The GitHub URL.
    :return: (domain, owner, repo_name) tuple.
    """
    ssh_pattern = r"^ssh://(?:git@)?(?P<domain>[\w.-]+)(?::|/)(?P<owner>[\w-]+)/(?P<repo>[\w.-]+)\.git$"
    https_pattern = r"https://(?P<domain>[\w.-]+)/(?P<owner>[\w-]+)/(?P<repo>[\w.-]+)"

    if match := re.match(ssh_pattern, url):
        return match.group("domain"), match.group("owner"), match.group("repo")
    elif match := re.match(https_pattern, url):
        return match.group("domain"), match.group("owner"), match.group("repo")
    else:
        print(f"Error: Invalid GitHub repository URL: {url}")
        sys.exit(1)


def check_or_create_github_repo(github_repo_url, private=False, org=None, dry_run=False):
    """
    Checks if a GitHub repository exists and creates it if it doesn't.

    :param github_repo_url: URL of the GitHub repository.
    :param private: Boolean indicating if the repository should be private.
    :param org: Organization under which to create the repository.
    :param dry_run: Whether to perform a dry run.
    """
    domain, _, repo_name = parse_github_url(github_repo_url)

    # Determine owner to use for repo.
    owner = f"{org}" if org else ""

    # Check if the repository exists
    print(f"Checking if the repository {github_repo_url} exists...")
    repo_check_command = f"GH_HOST={domain} gh repo view {owner}/{repo_name} --json name"
    result = subprocess.run(repo_check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(f"Repository {repo_name} already exists.")
        return

    # Create the repository if it doesn't exist
    print(f"Creating GitHub repository: {repo_name}")
    private_flag = "--private" if private else "--public"
    create_command = f"GH_HOST={domain} gh repo create {owner}/{repo_name} {private_flag}"
    run_command(create_command, f"Failed to create GitHub repository: {repo_name}", dry_run)


def archive_repository(github_repo_url, dry_run=False):
    """Archives a GitHub repository."""
    domain, owner, repo_name = parse_github_url(github_repo_url)
    print(f"Archiving repository: {github_repo_url}")
    archive_command = f"GH_HOST={domain} gh repo archive {owner}/{repo_name} -y"
    run_command(archive_command, f"Failed to archive repository: {github_repo_url}", dry_run)


def import_repository(external_repo_url, github_repo_url, private=False, org=None, archive=False, dry_run=False):
    """
    Imports an external Git repository into a new GitHub repository.

    :param external_repo_url: URL of the external Git repository.
    :param github_repo_url: URL of the GitHub repository.
    :param private: Boolean indicating if the repository should be private.
    :param org: Organization under which to create the repository.
    :param archive: Whether to archive the repository after importing.
    :param dry_run: Whether to perform a dry run.
    """
    check_or_create_github_repo(github_repo_url, private=private, org=org, dry_run=dry_run)

    repo_name = external_repo_url.split("/")[-1].replace(".git", "")
    print(f"\n=== Importing repository: {repo_name} ===")
    run_command(f"git clone --bare {external_repo_url}", f"Failed to clone repository: {external_repo_url}", dry_run)

    if not dry_run:
        os.chdir(f"{repo_name}.git")

    run_command(f"git push --mirror {github_repo_url}", f"Failed to push repository: {github_repo_url}", dry_run)

    if not dry_run:
        os.chdir("..")
        run_command(f"rm -rf {repo_name}.git", f"Failed to remove temporary local repository: {repo_name}.git")

    if archive:
        archive_repository(github_repo_url, dry_run)


def process_repositories(repo_list, private=False, org=None, archive=False, dry_run=False):
    """
    Processes a list of repositories.

    :param repo_list: A list of tuples containing external and GitHub repo URLs.
    :param private: Whether repositories should be private.
    :param org: Organization under which to create the repositories.
    :param archive: Whether to archive repositories after importing.
    :param dry_run: Whether to perform a dry run.
    """
    for external_repo_url, github_repo_url in repo_list:
        import_repository(
            external_repo_url, github_repo_url, private=private, org=org, archive=archive, dry_run=dry_run
        )


def main():
    print("Provide repositories via a file with lines containing two URLs separated by a space (ex: external_repo_url github_repo_url).")
    file_path = input("Enter the file path: ").strip()

    if not os.path.isfile(file_path):
        print("Error: File not found. Please provide a valid file path.")
        sys.exit(1)

    private = input("For repositories that don't exist and need to be created, should they be made private? (yes/no): ").strip().lower() == "yes"
    org = input("For repositories that don't exist and need to be created, enter the GitHub organization (leave blank for personal account): ").strip() or None
    archive = input("Archive repositories after import? (yes/no): ").strip().lower() == "yes"
    dry_run = input("Enable dry run mode? (yes/no): ").strip().lower() == "yes"

    try:
        with open(file_path, "r") as file:
            repo_list = [line.strip().split() for line in file if line.strip()]
    except Exception as e:
        print(f"Error: Could not read the file. {e}")
        sys.exit(1)

    for pair in repo_list:
        if len(pair) != 2:
            print(f"Error: Invalid line format: {pair}. Each line must have exactly two URLs.")
            sys.exit(1)

    print("\nThe following actions will be performed:")
    for external, github in repo_list:
        print(f"- Import {external} -> {github}")
        if archive:
            print(f"  -> Archive {github}")
    if not dry_run:
        confirm = input("\nDo you want to proceed? (yes/no): ").strip().lower() == "yes"
        if not confirm:
            print("Operation canceled.")
            sys.exit(0)

    process_repositories(repo_list, private=private, org=org, archive=archive, dry_run=dry_run)


if __name__ == "__main__":
    main()
