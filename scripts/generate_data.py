"""Sinh dữ liệu bằng Java để giữ một nguồn sinh dữ liệu và seed nhất quán."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(["java", "-cp", str(ROOT / "build"), "Main", "generate", str(ROOT / "data" / "generated"), "20261116"], check=True)

