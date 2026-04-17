# Copilot SDK + Agent Framework Installation on in01

## Summary
- Use Python 3.11 on in01.
- Create and use a virtual environment to avoid conflicts.
- Do not install globally, because org copilot already exists in PATH.
- In this environment, copilot-sdk package name is not available directly from pip.
- Installing agent-framework-github-copilot with --pre pulls github-copilot-sdk automatically.

## Step-by-Step

1. SSH to in01
```bash
ssh in01
```

2. Confirm Python 3.11 exists
```bash
python3.11 --version
```
Expected: Python 3.11.x

3. Create a dedicated virtual environment
```bash
python3.11 -m venv ~/venvs/copilot-sdk-311
```

4. Upgrade packaging tools inside venv
```bash
~/venvs/copilot-sdk-311/bin/python -m pip install --upgrade pip setuptools wheel
```

5. Install framework package (this also installs GitHub Copilot SDK dependency)
```bash
~/venvs/copilot-sdk-311/bin/python -m pip install --pre agent-framework-github-copilot
```

6. Verify installed package versions
```bash
~/venvs/copilot-sdk-311/bin/pip show github-copilot-sdk agent-framework-github-copilot
```

7. Verify imports from venv Python
```bash
~/venvs/copilot-sdk-311/bin/python -c 'import copilot, agent_framework_github_copilot; print(copilot.__file__)'
```
Expected: path under ~/venvs/copilot-sdk-311/lib64/python3.11/site-packages/

8. Verify package versions and install locations (including Agent Framework)
```bash
~/venvs/copilot-sdk-311/bin/pip show agent-framework-core agent-framework-github-copilot github-copilot-sdk
```

9. Verify module paths explicitly
```bash
~/venvs/copilot-sdk-311/bin/python -c 'import agent_framework, agent_framework_github_copilot, copilot; print(agent_framework.__file__); print(agent_framework_github_copilot.__file__); print(copilot.__file__)'
```

10. Check GitHub Copilot CLI version (SDK bundled binary, not org copilot)
```bash
/u/trankiet/venvs/copilot-sdk-311/lib64/python3.11/site-packages/copilot/bin/copilot --version
```

## Important Notes
- Org command copilot points to Synopsys tool in PATH.
- Running copilot --version (without full path) fails because this org tool expects a subtool name.
- This is expected and does not indicate SDK install failure.
- Use the full SDK binary path to check GitHub Copilot CLI version.
- Check Python package versions with venv pip show.

## Optional Daily Usage
- Activate environment:
```bash
source ~/venvs/copilot-sdk-311/bin/activate
```
- Or run venv python directly without activation.