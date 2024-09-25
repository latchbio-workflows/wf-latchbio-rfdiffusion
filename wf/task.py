import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from latch.executions import rename_current_execution
from latch.resources.tasks import small_gpu_task, v100_x1_task
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile

sys.stdout.reconfigure(line_buffering=True)


@v100_x1_task
def task(
    run_name: str,
    output_directory: LatchOutputDir,
    num_designs: int,
    contig_string: str,
    # design_type: str,
    input_pdb: Optional[LatchFile],
    symmetry: Optional[str],
    scaffold_dir: Optional[LatchDir],
    guiding_potentials: Optional[str],
    hotspot_residues: Optional[str],
    ckpt_override_path: Optional[LatchFile],
    scaffold_guided: bool = False,
    mask_loops: bool = False,
    partial_diffusion: bool = False,
    partial_T: int = 20,
    noise_scale_ca: float = 1.0,
    noise_scale_frame: float = 1.0,
    final_step: int = 50,
) -> LatchOutputDir:
    rename_current_execution(str(run_name))

    print("-" * 60)
    print("Creating local directories")
    local_output_dir = Path(f"/root/outputs/{run_name}")
    local_output_dir.mkdir(parents=True, exist_ok=True)

    print("-" * 60)
    subprocess.run(["nvidia-smi"], check=True)
    subprocess.run(["nvcc", "--version"], check=True)

    print("Running ProteinMPNN")
    command = [
        "/root/miniconda/bin/conda",
        "run",
        "--name",
        "SE3nv",
        "python",
        "/tmp/docker-build/work/RFdiffusion/scripts/run_inference.py",
        f"contigmap.contigs=[{contig_string}]",
        f"inference.output_prefix={local_output_dir}/{run_name}",
        f"inference.num_designs={num_designs}",
    ]
    try:
        subprocess.run(command, check=True)
    except Exception as e:
        print("FAILED")
        print(e)
        time.sleep(6000)

    print("Returning results")
    return LatchOutputDir(str("/root/outputs"), output_directory.remote_path)
