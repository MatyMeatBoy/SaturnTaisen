"""Compile and run the offline RetroAchievements integration tests in a temporary build."""
import argparse
from pathlib import Path
import os
import subprocess
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rcheevos", type=Path, required=True, help="local rcheevos 12.5.0 source directory")
    parser.add_argument("--sdk", type=Path, help="patched SDK directory (default local/deps/satrecomp)")
    parser.add_argument("--toolchain", type=Path, default=Path("C:/msys64/clang64"))
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    sdk = (args.sdk or source.parents[1] / "local/deps/satrecomp").resolve()
    upstream = args.rcheevos.resolve()
    if not (upstream / "include/rc_client.h").is_file():
        parser.error("--rcheevos must name an extracted rcheevos 12.5.0 source directory")
    if not (sdk / "cmake/sakura_ra.cmake").is_file():
        parser.error("apply the SaturnTaisen SDK patches before running this test")

    compiler = args.toolchain.resolve() / "bin"
    env = dict(os.environ, PATH=str(compiler) + os.pathsep + os.environ["PATH"])
    with TemporaryDirectory(prefix="saturntaisen-tra-tests-") as out:
        subprocess.run([str(compiler / "cmake.exe"), "-S", str(source), "-B", out, "-G", "Ninja",
                        "-DCMAKE_BUILD_TYPE=Release",
                        f"-DCMAKE_C_COMPILER={compiler / 'clang.exe'}",
                        f"-DCMAKE_CXX_COMPILER={compiler / 'clang++.exe'}",
                        f"-DSATRECOMP_SOURCE_DIR={sdk}",
                        f"-DFETCHCONTENT_SOURCE_DIR_RCHEEVOS={upstream}"], env=env, check=True)
        subprocess.run([str(compiler / "cmake.exe"), "--build", out, "--parallel", "2"], env=env, check=True)
        subprocess.run([str(compiler / "ctest.exe"), "--test-dir", out, "--output-on-failure"], env=env, check=True)


if __name__ == "__main__":
    main()
