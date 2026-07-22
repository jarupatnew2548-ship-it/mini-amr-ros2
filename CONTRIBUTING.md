# Contributing to Mini-AMR ROS 2

Thanks for your interest in contributing! This project is a simulated
Autonomous Mobile Robot (AMR) stack for **ROS 2 Jazzy** on **Ubuntu 24.04**.
The guidelines below keep the workspace clean and reproducible.

## Getting started

1. **Fork** the repository and clone your fork.
2. Place the workspace so the packages live under `src/`, then build:
   ```bash
   cd amr_ws
   colcon build
   source install/setup.bash
   ```
3. Verify the demos still run (see [`README.md`](README.md)):
   ```bash
   ros2 launch mini_amr_navigation navigation.launch.py
   ```

## Development workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/short-description
   ```
2. Make focused changes with clear, descriptive commit messages.
3. Rebuild and test the affected launch files before opening a PR.
4. Push your branch and open a **Pull Request** against `main`, describing
   *what* changed and *why*.

## Coding guidelines

- **Language:** Python 3.12 (ament_python packages).
- **Style:** follow PEP 8; the packages ship `ament_flake8` / `ament_pep257`
  tests — run them before submitting:
  ```bash
  colcon test --packages-select <package_name>
  colcon test-result --verbose
  ```
- **Nodes:** one responsibility per node; use ROS parameters instead of
  hard-coded values where practical.
- **Launch files:** resolve package resources with `FindPackageShare` — never
  hard-code absolute paths such as `/home/<user>/...`.
- **Frames & TF:** keep the TF tree consistent
  (`map → odom → base_footprint → base_link → …`); do not introduce a second
  publisher for a transform that another node already provides.

## What NOT to commit

The following are build artifacts and are excluded via `.gitignore` —
please do not add them:

- `build/`, `install/`, `log/`
- `__pycache__/`, `*.pyc`, `*.egg-info/`
- editor/IDE folders (`.vscode/`, `.idea/`) and OS files (`.DS_Store`)
- large binaries or archives (`*.zip`, rosbags)

Run `git status` before committing and confirm only intended files are staged.

## Reporting issues

Open a GitHub **Issue** and include:

- ROS 2 distribution and OS version,
- the exact command you ran,
- expected vs. actual behaviour,
- relevant log output (`/tmp/*.log`, terminal output, or RViz screenshots).

## License

By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE), the same license that covers this project.
