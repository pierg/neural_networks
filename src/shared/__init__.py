from pathlib import Path

# Path to the current file
this_file: Path = Path(__file__)

# Path to the main repo folder
main_repo_folder: Path = this_file.parent.parent.parent

# Path to configuration folder
config_folder: Path = main_repo_folder / "config"

# Path to configuration file
config_file: Path = config_folder / "configurations.toml"

# Path to results folder
results_folder: Path = main_repo_folder / "results"

# Tensorboard log directory
tb_log_dir: Path = main_repo_folder / "logs"