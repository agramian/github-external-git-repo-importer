# GitHub External Git Repo Importer

A Python script to automate the import of external Git repositories into GitHub, with support for creating destination repositories on-the-fly using the GitHub CLI.

The script uses the procedure described in the official GitHub doc for [Importing an external Git repository using the command line](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/importing-an-external-git-repository-using-the-command-line)

## Features
- Imports multiple external Git repositories into GitHub.
- Automatically creates the destination repositories if they don’t exist.
- Supports private repositories and organization accounts.
- Supports archiving repositories after import.
- Cleans up temporary files after import.

## Requirements
- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated.
- Python 3.7+.
- Git installed.

## Usage
1. Make sure the GitHub CLI is authenticated:

        gh auth login

1. Prepare a file listing the external and GitHub repositories, one pair per line (ex: `external_repo_url github_repo_url`).
   
   Example `repositories.txt`:

        https://external-host.com/extuser/repo1.git https://github.com/ghuser/repo1.git
        https://external-host.com/extuser/repo2.git https://github.com/orgname/repo2.git
        ssh://git@external-host.com/extuser/repo3.git ssh://git@github.com/ghuser/repo3.git
        # If the "ssh://" prefix is not included on the url,
        # note the different separator (":" vs "/") after the domain.
        git@external-host.com:extuser/repo4.git git@github.com:ghuser/repo4.git

1. Run the script

        python github-external-git-repo-importer.py

    *Note: some systems may require explicitly using `python3` to ensure Python 3 is used to run the script.*
1. Follow the prompts:
   - Enter the file path for the repositories list.
   - Specify whether to make the GitHub repositories private.
   - Optionally, provide the name of the GitHub organization.
   - Specify whether to archive the GitHub repositories after import.
   - Specify whether to execute the script in dry mode to preview the actions.
1. Output:
   - Repositories imported to GitHub.
   - Temporary local files cleaned up.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
