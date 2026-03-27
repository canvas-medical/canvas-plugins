# Contributing to Canvas

First off, thank you for considering contributing to this project! We appreciate your time and effort in helping improve the project. To make the process as smooth as possible, please follow the guidelines below.

## Table of Contents
1. [Getting Started](#getting-started)
2. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Proposing Features](#proposing-features)
   - [Code Contributions](#code-contributions)
3. [Commit Message Guidelines](#commit-message-guidelines)
4. [Pull Request Process](#pull-request-process)
5. [Code of Conduct](#code-of-conduct)

---

## Getting Started

To get started contributing to this project:
1. Fork the repository.
2. Clone your fork: `git clone https://github.com/your-username/canvas-plugins.git`.
3. Create a new branch for your feature: `git checkout -b feature/your-feature-name`.
4. After making changes, push your branch: `git push origin feature/your-feature-name`.
5. Submit a pull request following the [Pull Request Process](#pull-request-process).

---

## How to Contribute

### Reporting Bugs

If you encounter a bug, please open an issue and include:
- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected and actual results.
- Any relevant logs, screenshots, or error messages.

### Proposing Features

We welcome feature requests! To propose a new feature:
- Check if there's an existing issue or pull request for it.
- Open an issue with a detailed description of the feature.
- If you’d like to implement it, let us know, and we’ll work with you on it.

### Code Contributions

We appreciate all forms of contributions, including documentation, bug fixes, new features, and more! When contributing code:
1. Ensure your code follows the project's coding style.
2. Write tests to cover your changes where applicable.
3. Make sure your code builds and passes the existing tests.

---

## Commit Message Guidelines

We follow the **Conventional Commits** specification for our commit messages. This is important because it allows us to automate the release process and generate changelogs from the commit history.

Here’s the format to use:

```
<type>(<scope>): <subject>
```

**Type**: The type of change you're committing. Allowed values:
- `feat`: A new feature.
- `fix`: A bug fix.
- `docs`: Documentation updates.
- `refactor`: Code restructuring, without adding features or fixing bugs.
- `test`: Adding or updating tests.
- `chore`: Changes to the build process or auxiliary tools and libraries.

**Scope**: (Optional) The area of the codebase affected (e.g., `sdk`, `commands`, `ci`).

**Subject**: A short description of the change.

---

## Pull Request Process

1. Ensure your PR is based on the latest `main` branch.
2. Follow the [Commit Message Guidelines](#commit-message-guidelines).
3. Make sure all tests pass locally.
4. Submit your pull request and fill in the description template.
5. Wait for code reviews from the maintainers.
6. After approval, your PR will be merged following our release process.

---

## Hotfix Release Process

To release a patch fix for a previous version without including unreleased features from `main`:

1. **Create a release branch** from the version tag:
   ```bash
   git checkout -b release/0.122.x 0.122.0
   git push origin release/0.122.x
   ```

2. **Cherry-pick the fix** onto the release branch:
   ```bash
   git cherry-pick <commit-sha>
   git push origin release/0.122.x
   ```

3. **Trigger the release** from GitHub Actions:
   - Go to Actions > "Semantic Release" workflow
   - Click "Run workflow"
   - Select branch `release/0.122.x`
   - Optionally run with dry-run first to verify

4. The workflow forces a patch bump on release branches, so it will produce `0.122.1` regardless of commit type.

**Notes:**
- Use the naming convention `release/X.Y.x` (e.g., `release/0.122.x`)
- Multiple patches can be released from the same branch (0.122.1, 0.122.2, etc.)
- Always merge the fix to `main` as well to ensure it's included in future releases
- Only use a release branch when `main` has unreleased features you want to exclude. If `main` has no pending features, just release from `main` directly.

---

## Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code and maintain a respectful and collaborative environment.
