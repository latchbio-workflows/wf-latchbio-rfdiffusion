import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from latch.executions import rename_current_execution
from latch.resources.tasks import small_gpu_task, v100_x1_task
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile

sys.stdout.reconfigure(line_buffering=True)


class SymmetryType(Enum):
    CYCLIC_4 = "C4"
    CYCLIC_6 = "C6"
    DIHEDRAL_2 = "D2"
    DIHEDRAL_4 = "D4"
    TETRAHEDRAL = "tetrahedral"


class PotentialDecayType(Enum):
    CONSTANT = "constant"
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    CUBIC = "cubic"


@v100_x1_task
def rfdif_task(
    run_name: str,
    output_directory: LatchOutputDir,
    num_designs: int,
    contig_string: str,
    contig_length: Optional[str] = None,
    contig_provide_seq: Optional[str] = None,
    input_pdb: Optional[LatchFile] = None,
    hotspot_residues_binder: Optional[str] = None,
    hotspot_residues_motif: Optional[str] = None,
    hotspot_residues_ppi: Optional[str] = None,
    scaffold_dir: Optional[LatchDir] = None,
    target_path: Optional[LatchFile] = None,
    target_ss: Optional[LatchFile] = None,
    target_adj: Optional[LatchFile] = None,
    symmetry_gen: Optional[SymmetryType] = None,
    symmetry_motif: Optional[SymmetryType] = None,
    partial_T: Optional[int] = None,
    final_step: int = 50,
    noise_scale_ca: float = 1.0,
    noise_scale_frame: float = 1.0,
    guiding_potentials: Optional[List[str]] = None,
    ckpt_override_path: Optional[LatchFile] = None,
    potentials_olig_intra_all: bool = False,
    potentials_olig_inter_all: bool = False,
    potentials_guide_scale: float = 1.0,
    potentials_substrate: Optional[str] = None,
    potentials_guide_decay: PotentialDecayType = PotentialDecayType.CONSTANT,
    contig_inpaint_str_strand: Optional[str] = None,
    contig_inpaint_str_helix: Optional[str] = None,
    contig_inpaint_str: Optional[str] = None,
    scaffoldguided: bool = False,
    scaffoldguided_mask_loops: bool = False,
    scaffoldguided_target_pdb: bool = False,
) -> LatchOutputDir:
    rename_current_execution(str(run_name))

    print("-" * 60)
    print("Creating local directories")
    local_output_dir = Path(f"/root/outputs/{run_name}")
    local_output_dir.mkdir(parents=True, exist_ok=True)

    print("-" * 60)
    subprocess.run(["nvidia-smi"], check=True)
    subprocess.run(["nvcc", "--version"], check=True)

    print("Running RFdiffusion")
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

    if input_pdb:
        command.append(f"inference.input_pdb={input_pdb.local_path}")

    if contig_length:
        command.append(f"contigmap.length=[{contig_length}]")

    if contig_provide_seq:
        command.append(f"contigmap.provide_seq=[{contig_provide_seq}]")

    if contig_inpaint_str:
        command.append(f"contigmap.inpaint_str=[{contig_inpaint_str}]")

    if contig_inpaint_str_helix:
        command.append(f"contigmap.inpaint_str_helix=[{contig_inpaint_str_helix}]")

    if contig_length:
        command.append(f"contigmap.length={contig_length}")

    if hotspot_residues_binder:
        command.append(f"ppi.hotspot_res=[{hotspot_residues_binder}]")

    if hotspot_residues_motif:
        command.append(f"ppi.hotspot_res=[{hotspot_residues_motif}]")

    if hotspot_residues_ppi:
        command.append(f"ppi.hotspot_res=[{hotspot_residues_ppi}]")

    if scaffoldguided:
        command.append("scaffoldguided.scaffoldguided=True")

    if scaffoldguided_target_pdb:
        command.append("scaffoldguided.target_pdb=True")

    if scaffoldguided_mask_loops:
        command.append("scaffoldguided.mask_loops=True")

    if scaffold_dir:
        command.append(f"scaffoldguided.scaffold_dir={scaffold_dir.local_path}")
        if not scaffoldguided:
            command.append("scaffoldguided.scaffoldguided=True")

    if target_path:
        command.append(f"scaffoldguided.target_path={target_path.local_path}")
        if not scaffoldguided_target_pdb:
            command.append("scaffoldguided.target_pdb=True")

    if target_ss:
        command.append(f"scaffoldguided.target_ss={target_ss.local_path}")

    if target_adj:
        command.append(f"scaffoldguided.target_adj={target_adj.local_path}")

    # Handle symmetry options
    if symmetry_gen and symmetry_motif:
        if symmetry_gen != symmetry_motif:
            raise ValueError(
                "symmetry_gen and symmetry_motif must be the same if both are provided"
            )
        command.append(f"inference.symmetry={symmetry_gen.value}")
    elif symmetry_gen:
        command.append(f"inference.symmetry={symmetry_gen.value}")
    elif symmetry_motif:
        command.append(f"inference.symmetry={symmetry_motif.value}")

    if partial_T is not None:
        command.append(f"diffuser.partial_T={partial_T}")

    command.append(f"diffuser.T={final_step}")
    command.append(f"denoiser.noise_scale_ca={noise_scale_ca}")
    command.append(f"denoiser.noise_scale_frame={noise_scale_frame}")

    # 'potentials.guiding_potentials=["type:olig_contacts,weight_intra:1,weight_inter:0.1"]' -> goal
    # 'potentials.guiding_potentials=["type:olig_contacts","weight_intra:1","weight_inter:0.1"]' -> now
    if guiding_potentials:
        potentials_str = ",".join(guiding_potentials)
        command.append(f'potentials.guiding_potentials=["{potentials_str}"]')

    if potentials_olig_intra_all:
        command.append("potentials.olig_intra_all=True")

    if potentials_olig_inter_all:
        command.append("potentials.olig_inter_all=True")

    if potentials_substrate:
        command.append(f"potentials.substrate={potentials_substrate}")

    command.append(f"potentials.guide_scale={potentials_guide_scale}")
    command.append(f"potentials.guide_decay={potentials_guide_decay.value}")

    if ckpt_override_path:
        command.append(f"inference.ckpt_override_path={ckpt_override_path.local_path}")

    try:
        print("RUNNING COMMAND: ")
        print(" ".join(command))
        subprocess.run(command, check=True)
    except Exception as e:
        print("FAILED")
        print(e)
    print("Returning results")
    return LatchOutputDir(str("/root/outputs"), output_directory.remote_path)
