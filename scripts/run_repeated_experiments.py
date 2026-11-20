from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
JAVA_HOME = os.environ.get("JAVA_HOME")
JAVA = str(Path(JAVA_HOME) / "bin" / "java.exe") if JAVA_HOME else "java"
JAVAC = str(Path(JAVA_HOME) / "bin" / "javac.exe") if JAVA_HOME else "javac"
BUILD = ROOT / "build"
DATA = ROOT / "data" / "generated"
OUT = ROOT / "results" / "repeated"
BATCHES = 5
REPEAT = 20
WARMUP = 3
BUILD.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
files = [str(path) for path in (ROOT / "src").rglob("*.java")]
subprocess.run([JAVAC, "-d", str(BUILD), *files], check=True)
for batch in range(1, BATCHES + 1):
    batch_dir = OUT / f"batch_{batch}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    for input_file in sorted(DATA.glob("*.txt")):
        output_file = batch_dir / f"{input_file.stem}.csv"
        seed = 20261116 + batch * 1009
        subprocess.run([JAVA, "-cp", str(BUILD), "Main", "benchmark", str(input_file), str(output_file), str(REPEAT), str(WARMUP), str(seed)], check=True)
