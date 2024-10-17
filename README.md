# RFdiffusion: Advanced Protein Structure Generation and Design

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
