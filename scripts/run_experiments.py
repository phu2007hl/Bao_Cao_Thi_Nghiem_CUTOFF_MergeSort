from pathlib import Path
import subprocess
import os

ROOT = Path(__file__).resolve().parents[1]
java_home = os.environ.get("JAVA_HOME")
javac = str(Path(java_home) / "bin" / "javac.exe") if java_home else "javac"
java = str(Path(java_home) / "bin" / "java.exe") if java_home else "java"
build_dir = ROOT / "build"
build_dir.mkdir(parents=True, exist_ok=True)
java_files = [str(path) for path in (ROOT / "src").rglob("*.java")]
subprocess.run([javac, "-d", str(build_dir), *java_files], check=True)
data_dir = ROOT / "data" / "generated"
out_dir = ROOT / "results" / "raw"
out_dir.mkdir(parents=True, exist_ok=True)
for input_file in sorted(data_dir.glob("*.txt")):
    output_file = out_dir / f"{input_file.stem}.csv"
    subprocess.run([java, "-cp", str(build_dir), "Main", "benchmark", str(input_file), str(output_file), "10", "3"], check=True)

