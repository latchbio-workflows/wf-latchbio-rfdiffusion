from typing import Optional

from latch.resources.workflow import workflow
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import (
    Fork,
    ForkBranch,
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
    LatchRule,
    Params,
    Section,
    Spoiler,
)

from wf.task import task

flow = [
    Section(
        "Input and Output",
        Params(
            "input_pdb",
            "run_name",
            "output_directory",
            "num_designs",
        ),
    ),
    Section(
        "Design Configuration",
        Params(
            "contig_string",
            "symmetry",
        ),
        Spoiler(
            "Scaffold-Guided Design",
            Params(
                "scaffold_guided",
                "scaffold_dir",
                "mask_loops",
            ),
        ),
        Spoiler(
            "Binder Design",
            Params(
                "hotspot_residues",
            ),
        ),
    ),
    Section(
        "Diffusion Parameters",
        Params(
            "final_step",
            "noise_scale_ca",
            "noise_scale_frame",
        ),
        Spoiler(
            "Partial Diffusion",
            Params(
                "partial_diffusion",
                "partial_T",
            ),
        ),
    ),
    Spoiler(
        "Advanced Options",
        Params(
            "guiding_potentials",
            "ckpt_override_path",
        ),
    ),
]


metadata = LatchMetadata(
    display_name="RFdiffusion",
    author=LatchAuthor(
        name="LatchBio",
    ),
    parameters={
        "run_name": LatchParameter(
            display_name="Run Name",
            description="Name of the run",
            batch_table_column=True,
            rules=[
                LatchRule(
                    regex=r"^[a-zA-Z0-9_-]+$",
                    message="Run name must contain only letters, digits, underscores, and dashes. No spaces are allowed.",
                )
            ],
        ),
        "output_directory": LatchParameter(
            display_name="Output Directory",
            description="Directory to save output files",
            batch_table_column=True,
        ),
        "contig_string": LatchParameter(
            display_name="Contig String",
            description="Contig string specifying protein design (e.g., '5-15/A10-25/30-40')",
            batch_table_column=True,
        ),
        "input_pdb": LatchParameter(
            display_name="Input PDB File",
            description="PDB file for motif scaffolding or binder design",
            batch_table_column=True,
        ),
        "num_designs": LatchParameter(
            display_name="Number of Designs",
            description="Number of designs to generate",
            batch_table_column=True,
        ),
        # "design_type": LatchParameter(
        #     display_name="Design Type",
        #     description="Type of protein design task",
        #     choices=[
        #         "unconditional",
        #         "motif_scaffolding",
        #         "binder_design",
        #         "symmetric_oligomer",
        #     ],
        #     batch_table_column=True,
        # ),
        "symmetry": LatchParameter(
            display_name="Symmetry Type",
            description="Type of symmetry for oligomer design",
            # choices=["none", "cyclic", "dihedral", "tetrahedral"],
            batch_table_column=True,
        ),
        "scaffold_guided": LatchParameter(
            display_name="Use Scaffold Guiding",
            description="Enable scaffold-guided design",
            batch_table_column=True,
        ),
        "scaffold_dir": LatchParameter(
            display_name="Scaffold Directory",
            description="Directory containing scaffold files for guided design",
            batch_table_column=True,
        ),
        "hotspot_residues": LatchParameter(
            display_name="Hotspot Residues",
            description="List of hotspot residues for binder design (e.g., 'A30,A33,A34')",
            batch_table_column=True,
        ),
        "mask_loops": LatchParameter(
            display_name="Mask Loops",
            description="Mask loops in scaffold-guided design",
            batch_table_column=True,
        ),
        "partial_diffusion": LatchParameter(
            display_name="Partial Diffusion",
            description="Enable partial diffusion for design diversification",
            batch_table_column=True,
        ),
        "partial_T": LatchParameter(
            display_name="Partial Diffusion Timestep",
            description="Timestep for partial diffusion (if enabled)",
            batch_table_column=True,
        ),
        "noise_scale_ca": LatchParameter(
            display_name="Noise Scale (CA)",
            description="Noise scale for translations",
            batch_table_column=True,
        ),
        "noise_scale_frame": LatchParameter(
            display_name="Noise Scale (Frame)",
            description="Noise scale for rotations",
            batch_table_column=True,
        ),
        "guiding_potentials": LatchParameter(
            display_name="Guiding Potentials",
            description="List of guiding potentials to use (e.g., 'monomer_ROG,olig_contacts')",
            batch_table_column=True,
        ),
        "final_step": LatchParameter(
            display_name="Final Diffusion Step",
            description="Final step for the diffusion trajectory",
            batch_table_column=True,
        ),
        "ckpt_override_path": LatchParameter(
            display_name="Checkpoint Override Path",
            description="Path to a specific model checkpoint (if needed)",
            batch_table_column=True,
        ),
    },
    flow=flow,
)


@workflow(metadata)
def rfdiffusion_workflow(
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
    return task(
        run_name=run_name,
        input_pdb=input_pdb,
        output_directory=output_directory,
        num_designs=num_designs,
        contig_string=contig_string,
        # design_type=design_type,
        symmetry=symmetry,
        scaffold_guided=scaffold_guided,
        scaffold_dir=scaffold_dir,
        hotspot_residues=hotspot_residues,
        mask_loops=mask_loops,
        partial_diffusion=partial_diffusion,
        partial_T=partial_T,
        noise_scale_ca=noise_scale_ca,
        noise_scale_frame=noise_scale_frame,
        guiding_potentials=guiding_potentials,
        final_step=final_step,
        ckpt_override_path=ckpt_override_path,
    )
