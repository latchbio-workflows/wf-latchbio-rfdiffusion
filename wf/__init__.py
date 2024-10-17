from typing import Optional, List
from enum import Enum

from latch.resources.workflow import workflow
from latch.resources.launch_plan import LaunchPlan
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import (
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
    LatchRule,
    Params,
    Section,
    Spoiler,
    Fork,
    ForkBranch,
    Text
)


from wf.task import task

class PotentialDecayType(Enum):
    CONSTANT = "constant"
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    CUBIC = "cubic"

class SymmetryType(Enum):
    CYCLIC_4 = "C4"
    CYCLIC_6 = "C6"
    DIHEDRAL_2 = "D2"
    DIHEDRAL_4 = "D4"
    TETRAHEDRAL = "tetrahedral"

flow = [
    Section(
        "General Parameters",
        Params(
            "run_name",
            "contig_string",
            "num_designs",
            "output_directory",
        )),
    Section(
        "Generation",
        Text("Generation in RFdiffusion focuses on creating new protein structures from scratch."),
        Fork(
            "generation",
            "Select generation method",
            UNCONDITIONAL=ForkBranch("Unconditional Protein Generation", Text("Creates novel protein structures without any specific constraints or input motifs. Only requires a `contig_string`.")), # just needs a contig_string
            SYMMETRIC_OLIGOMERS=ForkBranch("Symmetric Oligomers Generation",
                                           Text("Generates protein complexes with defined symmetry, such as cyclic, dihedral, or tetrahedral arrangements. This is done by symmetrising the noise we sample at t=T, and symmetrising the input at every timestep."),
                                           Params("symmetry_gen")),
        )
    ),
    Section(
        "Design",
        Text("Design in RFDiffusion involves modifying or creating proteins with specific functional or structural constraints."),
        Params(
            "input_pdb",
            "contig_length",
        ),
        Fork(
            "design",
            "Select design generation method",
            MOTIF_SCAFFOLDING=ForkBranch("Motif Scaffolding", Text("Incorporates a given structural motif into a larger protein scaffold, useful for designing proteins with specific functional elements. Only requires the above PDB file.")), # just needs a PDB
            BINDER_DESIGN=ForkBranch("Binder Design", Text("Creates protein binders that can interact with a specified target protein, often used for developing therapeutic proteins or research tools."),
                                     Params("hotspot_residues_binder")),
            FOLD_CONDITIONING_PPI=ForkBranch("Fold Conditioning (PPI)",
                                             Text("Designs protein-protein interactions (PPIs) while constraining the overall fold of the designed protein, allowing for more controlled interface design."),
                                             Params(
                                                "hotspot_residues_ppi",
                                                "target_path",
                                                "target_ss",
                                                "target_adj"),
                                                Spoiler(
                                                    "Inpaint Parameters",
                                                    Params("contig_inpaint_str",
                                                            "contig_inpaint_str_strand",
                                                            "contig_inpaint_str_helix")
                                                ),
                                                Spoiler(
                                                    "Scaffold Guided Parameters",
                                                    Params("scaffoldguided",
                                                            "scaffoldguided_target_pdb",
                                                            "scaffoldguided_mask_loops",
                                                            "scaffold_dir"))),
            SYMMETRIC_MOTIF_SCAFFOLDING=ForkBranch("Symmetric Motif Scaffolding",
                                                   Text("Combines motif scaffolding with symmetry generation to create symmetric protein complexes containing specific structural motifs."),
                                                   Params("symmetry_motif")),
            DESIGN_DIVERSIFICATION=ForkBranch("Design Diversification",
                                              Text("Generates variations of an existing protein design by partially perturbing and then refining its structure, useful for exploring design space around a promising candidate."),
                                              Params("partial_T",
                                                    "contig_provide_seq")),
        )
    ),
    Section(
        "Advanced Options",
        Spoiler(
            "Diffusion Parameters",
            Params(
                "final_step",
                "noise_scale_ca",
                "noise_scale_frame",
            ),
        ),
        Spoiler(
            "Auxiliary Potentials",
            Params("guiding_potentials",
                    "potentials_olig_intra_all",
                    "potentials_olig_inter_all",
                    "potentials_guide_scale",
                    "potentials_guide_decay",
                    "potentials_substrate"),
        ),
        Spoiler(
            "Model Checkpoint",
            Params("ckpt_override_path"),
        ),
    ),
]

# symmetry and hotspot_residues are duplicated
metadata = LatchMetadata(
    display_name="RFdiffusion",
    author=LatchAuthor(
        name="Watson, J.L., Juergens, D., Bennett, N.R. et al.",
    ),
    tags=["Protein Engineering"],
    parameters={
        "run_name": LatchParameter(
            display_name="Run Name",
            description="Name of the run",
            batch_table_column=False,
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
            batch_table_column=False,
        ),
        "num_designs": LatchParameter(
            display_name="Number of Designs",
            description="Number of designs to generate",
            batch_table_column=False,
        ),
        "contig_string": LatchParameter(
            display_name="Contig String",
            description="Contig string specifying protein design (e.g., '5-15/A10-25/30-40')",
            batch_table_column=False,
        ),
        "contig_length": LatchParameter(
            display_name="Contig Length",
            description="To ensure the length was always e.g. 55 residues, this can be specified with contigmap.length=55-55",
            batch_table_column=False,
        ),
        "contig_provide_seq": LatchParameter(
            display_name="Contig provide_seq",
            description="For partial diffusion, keep parts of the sequence of the diffused chain fixed. The contigmap.provide_seq input is zero-indexed, and you can provide a range (so 100-119 is an inclusive range of 20, unmasking the whole sequence of the peptide).",
            batch_table_column=False,
        ),
        "contig_inpaint_str_strand": LatchParameter(
            display_name="Contig inpaint_str_helix",
            description="Mask the structure on this peptide, but adopt a beta (strand) secondary structure:",
            batch_table_column=False,
        ),
        "contig_inpaint_str_helix": LatchParameter(
            display_name="Contig inpaint_str_helix",
            description="Mask the structure on this peptide, but adopt a helix secondary structure:",
            batch_table_column=False,
        ),
        "contig_inpaint_str": LatchParameter(
            display_name="Contig inpaint_str",
            description="Mask the 3D structure.",
            batch_table_column=False,
        ),
        "scaffoldguided": LatchParameter(
            display_name="Scaffold Guided",
            description="scaffoldguided.scaffoldguided",
            batch_table_column=False,
        ),
        "scaffoldguided_target_pdb": LatchParameter(
            display_name="Scaffold Guided target_pdb",
            description="Mask the 3D structure.",
            batch_table_column=False,
        ),
        "scaffoldguided_mask_loops": LatchParameter(
            display_name="Scaffold Guided mask_loops",
            description="scaffoldguided.mask_loops",
            batch_table_column=False,
        ),
        "input_pdb": LatchParameter(
            display_name="Input PDB File",
            description="PDB file for motif scaffolding or binder design",
            batch_table_column=False,
        ),

        # Duplicate param for symmetry
        "symmetry_motif": LatchParameter(
            display_name="Symmetry Type",
            description="Type of symmetry for oligomer design",
            batch_table_column=False,
        ),
        "symmetry_gen": LatchParameter(
            display_name="Symmetry Type",
            description="Type of symmetry for oligomer design",
            batch_table_column=False,
        ),

        # Duplicate param for hotspot residues
        "hotspot_residues_binder": LatchParameter(
            display_name="Hotspot Residues",
            description="List of hotspot residues for binder design (e.g., 'A30,A33,A34')",
            batch_table_column=False,
        ),
        "hotspot_residues_ppi": LatchParameter(
            display_name="Hotspot Residues",
            description="List of hotspot residues for PPI",
            batch_table_column=False,
        ),
        "scaffold_dir": LatchParameter(
            display_name="Scaffold Directory",
            description="Directory containing scaffold files for guided design",
            batch_table_column=False,
        ),
        "target_path": LatchParameter(
            display_name="Target PDB Path",
            description="Path to the target PDB file for fold conditioning",
            batch_table_column=False,
        ),
        "target_ss": LatchParameter(
            display_name="Target Secondary Structure",
            description="Path to target secondary structure file",
            batch_table_column=False,
        ),
        "target_adj": LatchParameter(
            display_name="Target Adjacency",
            description="Path to target adjacency file",
            batch_table_column=False,
        ),
        "partial_T": LatchParameter(
            display_name="Partial Diffusion Timestep",
            description="Timestep for partial diffusion (if enabled)",
            batch_table_column=False,
        ),
        "final_step": LatchParameter(
            display_name="Final Diffusion Step",
            description="Final step for the diffusion trajectory",
            batch_table_column=False,
        ),
        "noise_scale_ca": LatchParameter(
            display_name="Noise Scale (CA)",
            description="Noise scale for translations",
            batch_table_column=False,
        ),
        "noise_scale_frame": LatchParameter(
            display_name="Noise Scale (Frame)",
            description="Noise scale for rotations",
            batch_table_column=False,
        ),
        "guiding_potentials": LatchParameter(
            display_name="Guiding Potentials",
            description="List of guiding potentials to use (e.g., 'monomer_ROG,olig_contacts')",
            batch_table_column=False,
        ),
        "ckpt_override_path": LatchParameter(
            display_name="Checkpoint Override Path",
            description="Path to a specific model checkpoint (if needed)",
            batch_table_column=False,
        ),
        "potentials_olig_intra_all": LatchParameter(
            display_name="Apply Intra-Chain Potentials to All Residues",
            description="Apply intra-chain potentials to all residues in oligomer design",
            batch_table_column=False,
        ),

        "potentials_olig_inter_all": LatchParameter(
            display_name="Apply Inter-Chain Potentials to All Residues",
            description="Apply inter-chain potentials to all residues in oligomer design",
            batch_table_column=False,
        ),

        "potentials_guide_scale": LatchParameter(
            display_name="Guiding Potential Scale",
            description="Scale factor for guiding potentials",
            batch_table_column=False,
        ),

        "potentials_guide_decay": LatchParameter(
            display_name="Guiding Potential Decay",
            description="Decay type for guiding potentials (e.g., quadratic)",
            batch_table_column=False,
        ),

        "potentials_substrate": LatchParameter(
            display_name="Potentials Substrate",
            description="Global option for potentials.substrate",
            batch_table_column=False,
        ),
    },
    flow=flow,
)

@workflow(metadata)
def rfdiffusion_workflow(
    run_name: str,
    contig_string: str,
    output_directory: LatchOutputDir = LatchOutputDir("latch:///RFDiffusion"),
    num_designs: int = 5,
    generation: str = "UNCONDITIONAL",
    design: str = "MOTIF_SCAFFOLDING",
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
    """RFdiffusion: Advanced Protein Structure Generation and Design

    <p align="center">
        <img src="https://github.com/RosettaCommons/RFdiffusion/raw/main/img/diffusion_protein_gradient_2.jpg" alt="RFdiffusion protein gradient" width="800px"/>
    </p>

    # RFdiffusion

    RFdiffusion is a cutting-edge, open-source method for protein structure generation and design. It leverages diffusion models, a class of deep generative models, to create novel protein structures with or without conditional information such as motifs or targets. Developed by a team of researchers from the University of Washington, RFdiffusion builds upon the architecture and trained parameters of RoseTTAFold, extending its capabilities to address a wide range of protein engineering challenges.

    ## Key Features and Capabilities

    RFdiffusion operates in two main branches: Generation and Design.

    ### Generation

    <p align="center">
        <img src="https://github.com/RosettaCommons/RFdiffusion/raw/main/img/cropped_uncond.png" alt="RFdiffusion protein gradient" width="300px"/>
    </p>

    1. **Unconditional Protein Generation**: Creates entirely new protein structures without specific constraints, allowing for the exploration of novel folds and architectures.
    2. **Symmetric Oligomers Generation**: Produces protein complexes with defined symmetry arrangements, including cyclic, dihedral, and tetrahedral symmetries, enabling the design of complex multi-subunit proteins.

    ### Design

    <p align="center">
        <img src="https://github.com/RosettaCommons/RFdiffusion/raw/main/img/binder.png" alt="RFdiffusion protein gradient" width="300px"/>
    </p>

    1. **Motif Scaffolding**: Incorporates given structural motifs into larger protein scaffolds, useful for designing proteins with specific functional elements or binding sites.
    2. **Binder Design**: Creates proteins that can interact with specified target proteins, facilitating the development of therapeutic proteins, research tools, or protein-based sensors.
    3. **Fold Conditioning - PPI**: Designs protein-protein interactions while constraining the overall fold of the designed protein, allowing for more controlled interface design.
    4. **Symmetric Motif Scaffolding**: Combines motif scaffolding with symmetry generation to create symmetric protein complexes containing specific structural motifs.
    5. **Design Diversification**: Generates variations of an existing protein design by partially perturbing and then refining its structure, useful for exploring the design space around promising candidates.

    ## Key Parameters

    RFdiffusion offers a wide range of parameters to control the generation and design process:

    1. `Run Name` A unique identifier for each run, used for organizing outputs.
    2. `Output Directory` The location where all output files will be saved.
    3. `Number of Designs` The number of protein designs to generate in a single run.
    4. `Contig String` Specifies the protein design, including motifs and connecting regions (e.g., '5-15/A10-25/30-40').
    5. `Input PDB File` The starting structure for motif scaffolding or binder design tasks.
    6. `Symmetry Type` Specifies the type of symmetry for oligomer design (e.g., cyclic, dihedral, tetrahedral).
    7. `Hotspot Residues` Key residues on the target protein that guide binder design.
    8. `Scaffold Directory` Contains pre-computed scaffold files for guided design tasks.
    9. `Target PDB Path` The structure file of the target protein for fold conditioning in protein-protein interaction design.
    10. `Target Secondary Structure and Adjacency` Files specifying the desired secondary structure and residue adjacency for fold conditioning.
    11. `Partial Diffusion Timestep` Controls the amount of noise added in partial diffusion for design diversification.
    12. `Final Diffusion Step` Determines when to stop the diffusion trajectory, potentially speeding up inference.
    13. `Noise Scales` Control the amount of noise used during sampling for translations (CA) and rotations (Frame).
    14. `Guiding Potentials` Additional constraints or objectives to guide the generation process (e.g., 'monomer_ROG,olig_contacts').
    15. `Checkpoint Override Path` Allows the use of specific model weights for specialized tasks.

    ## Outputs

    RFdiffusion generates several output files for each design:

    1. `PDB File`: The final predicted protein structure. Note that designed residues are output as glycine backbones without side chains.
    2. `TRB File`: Contains metadata associated with the specific run, including:
    - The full configuration used by RFdiffusion
    - Mapping details (how input residues correspond to output residues)
    - Information about any masked residues during inference
    3. `Trajectory Files`: Found in the `/traj/` folder, these files show the full diffusion process:
    - Can be viewed as multi-step PDFs in PyMOL
    - Include both `pX0` predictions (model predictions at each timestep) and `Xt-1` trajectories (inputs to the model at each timestep)
    - Ordered in reverse, with the first PDB being the last prediction made during inference

    ## Advanced Features

    - `Auxiliary Potentials`: RFdiffusion allows the use of additional guiding forces during the diffusion process, enabling more control over the final structure (e.g., enforcing well-packed proteins).
    - `Flexible Peptide Design`: The tool can design binders to flexible peptides where the 3D coordinates are not specified, but the secondary structure can be defined.
    - `Active Site Model`: A specialized model for scaffolding very small motifs, such as enzyme active sites, with improved precision.

    ## Practical Considerations

    - `Target Site Selection`: For binder design, choose sites with multiple hydrophobic residues and avoid highly charged or glycosylated areas.
    - `Target Truncation`: For large targets, truncate the protein to reduce computational complexity while preserving the binding site and essential structure.
    - `Hotspot Selection`: Choose 3-6 hotspot residues to guide binder design, running pilot studies to optimize selection.
    - `Scale`: While large campaigns may generate thousands of designs, smaller runs of ~1,000 backbones may suffice for many targets.
    - `Sequence Design`: RFdiffusion generates backbones only. Use tools like ProteinMPNN for sequence design.
    - `Filtering`: Use structure prediction tools like AlphaFold2 to evaluate designs, filtering for those with predicted accurate binding (pAE_interaction < 10).

    RFdiffusion represents a significant advance in computational protein design, offering a versatile and powerful tool for researchers in structural biology, drug design, and synthetic biology. Its ability to generate novel proteins and complexes with specific structural and functional properties opens up new possibilities in protein engineering and biotechnology.

    ## Citations

    If you use RFdiffusion in your research, please cite:

    [RFdiffusion paper](https://www.biorxiv.org/content/10.1101/2022.12.09.519842v1)

    ## License

    RFdiffusion is released under an open source BSD License. It is free for both non-profit and for-profit use.

    ## Acknowledgements

    RFdiffusion builds directly on the architecture and trained parameters of RoseTTAFold. We thank Frank DiMaio and Minkyung Baek, who developed RoseTTAFold.

    ## Contact

    For help and support, please create GitHub issues on the [RFdiffusion repository](https://github.com/RosettaCommons/RFdiffusion).

    ---

    <p align="center">
        <img src="https://github.com/RosettaCommons/RFdiffusion/raw/main/img/partial.png" alt="RFdiffusion protein gradient" width="300px"/>
    </p>



    """
    return task(
        run_name=run_name,
        output_directory=output_directory,
        num_designs=num_designs,
        contig_string=contig_string,
        contig_length=contig_length,
        contig_provide_seq=contig_provide_seq,
        input_pdb=input_pdb,
        hotspot_residues_binder=hotspot_residues_binder,
        hotspot_residues_motif=hotspot_residues_motif,
        hotspot_residues_ppi=hotspot_residues_ppi,
        scaffold_dir=scaffold_dir,
        target_path=target_path,
        target_ss=target_ss,
        target_adj=target_adj,
        symmetry_gen=symmetry_gen,
        symmetry_motif=symmetry_motif,
        partial_T=partial_T,
        final_step=final_step,
        noise_scale_ca=noise_scale_ca,
        noise_scale_frame=noise_scale_frame,
        guiding_potentials=guiding_potentials,
        ckpt_override_path=ckpt_override_path,
        potentials_olig_intra_all=potentials_olig_intra_all,
        potentials_olig_inter_all=potentials_olig_inter_all,
        potentials_guide_scale=potentials_guide_scale,
        potentials_guide_decay=potentials_guide_decay,
        contig_inpaint_str_strand=contig_inpaint_str_strand,
        contig_inpaint_str_helix=contig_inpaint_str_helix,
        contig_inpaint_str=contig_inpaint_str,
        scaffoldguided=scaffoldguided,
        scaffoldguided_mask_loops=scaffoldguided_mask_loops,
        scaffoldguided_target_pdb=scaffoldguided_target_pdb,
        potentials_substrate=potentials_substrate
    )


LaunchPlan(
    rfdiffusion_workflow,
    "Symmetric Oligomers Generation: design_cyclic_oligos",
    {
        "run_name": "design_cyclic_oligos",
        "contig_string": "480-480",
        "num_designs": 10,
        "potentials_olig_inter_all": True,
        "potentials_olig_intra_all": True,
        "symmetry_gen": SymmetryType.CYCLIC_6,
        "guiding_potentials": ["type:olig_contacts", "weight_intra:1", "weight_inter:0.1"],
        "potentials_guide_scale": 2.0,
        "potentials_guide_decay": PotentialDecayType.QUADRATIC,
        "generation": "SYMMETRIC_OLIGOMERS"
    }
)


LaunchPlan(
    rfdiffusion_workflow,
    "Unconditional Protein Generation: design_unconditional",
    {
        "run_name": "design_unconditional",
        "contig_string": "100-200",
        "num_designs": 10,
        "generation": "UNCONDITIONAL"
    }
)

LaunchPlan(
    rfdiffusion_workflow,
    "Motif Scaffolding: design_motifscaffolding",
    {
        "run_name": "design_motifscaffolding",
        "contig_string": "10-40/A163-181/10-40",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/5TPN.pdb"),
        "num_designs": 10,
        "design": "MOTIF_SCAFFOLDING"
    }
)

LaunchPlan(
    rfdiffusion_workflow,
    "Motif Scaffolding: design_motifscaffolding_with_target",
    {
        "run_name": "design_motifscaffolding_with_target",
        "contig_string": "A25-109/0 0-70/B17-29/0-70",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/1YCR.pdb"),
        "num_designs": 2,
        "contig_length": "70-120",
        "design": "MOTIF_SCAFFOLDING"
    }
)

LaunchPlan(
    rfdiffusion_workflow,
    "Motif Scaffolding: design_enzyme",
    {
        "run_name": "design_enzyme",
        "contig_string": "10-100/A1083-1083/10-100/A1051-1051/10-100/A1180-1180/10-100",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/5an7.pdb"),
        "num_designs": 2,
        "potentials_guide_scale": 1.0,
        "guiding_potentials": ["type:substrate_contacts", "s:1,r_0:8", "rep_r_0:5.0", "rep_s:2", "rep_r_min:1"],
        "potentials_substrate": "LLK",
        "design": "MOTIF_SCAFFOLDING"
    }
)


LaunchPlan(
    rfdiffusion_workflow,
    "Design Diversification: design_partialdiffusion",
    {
        "run_name": "design_partialdiffusion",
        "contig_string": "79-79",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/2KL8.pdb"),
        "num_designs": 2,
        "partial_T": 10,
        "design": "DESIGN_DIVERSIFICATION"
    }
)


LaunchPlan(
    rfdiffusion_workflow,
    "Design Diversification: design_partialdiffusion_multipleseq",
    {
        "run_name": "design_partialdiffusion_multipleseq",
        "contig_string": "172-172/0 34-34",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/peptide_complex_ideal_helix.pdb"),
        "num_designs": 2,
        "partial_T": 10,
        "contig_provide_seq": "172-177,200-205",
        "design": "DESIGN_DIVERSIFICATION"
    }
)


LaunchPlan(
    rfdiffusion_workflow,
    "Fold Conditioning - PPI: design_ppi",
    {
        "run_name": "design_ppi",
        "contig_string": "A1-150/0 70-100",
        "hotspot_residues_ppi": "A59,A83,A91",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/insulin_target.pdb"),
        "num_designs": 2,
        "noise_scale_ca": 0.0,
        "noise_scale_frame": 0.0,
        "design": "FOLD_CONDITIONING_PPI"
    }
)

LaunchPlan(
    rfdiffusion_workflow,
    "Fold Conditioning - PPI: design_ppi_flexible_peptide_with_secondarystructure_specification",
    {
        "run_name": "design_ppi_flexible_peptide_with_secondarystructure_specification",
        "contig_string": "70-100/0 B165-178",
        "input_pdb": LatchFile("s3://latch-public/test-data/36431/examples/tau_peptide.pdb"),
        "num_designs": 2,
        "contig_inpaint_str": "B165-178",
        "scaffoldguided": True,
        "contig_inpaint_str_helix": "B165-178",
        "design": "FOLD_CONDITIONING_PPI"
    }
)

