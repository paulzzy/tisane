from os import link
from tisane.variable import AbstractVariable
from tisane.family import AbstractFamily, AbstractLink
from tisane.random_effects import RandomEffect
from tisane.graph import Graph
from tisane.graph_inference import infer_main_effects, infer_interaction_effects, infer_random_effects
from tisane.family_link_inference import infer_family_functions, infer_link_functions
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.code_generator import *
from tisane.gui.gui import TisaneGUI

from enum import Enum
from typing import List, Set, Dict
import copy
from pathlib import Path
from itertools import chain, combinations
import pandas as pd
import networkx as nx
import json

# Checks that the IVS for @param design have a conceptual relationship with the DV
# Issues a warning if an independent variable does not cause or associate with the DV
def check_design_ivs(design: Design):
    dv = design.dv
    for i in design.ivs:
        has_cause = design.graph.has_edge(start=i, end=dv, edge_type="cause")
        has_associate = design.graph.has_edge(start=i, end=dv, edge_type="associate")

        # Variable i has neither a cause nor an associate relationship with the DV
        if not has_cause and not has_associate:
            raise ValueError(
                f"The independent variable {i.name} does not have a conceptual relationship with the dependent variable {dv.name}. Every independent variable should either CAUSE or  ASSOCIATE_WITH the dependent variable."
            )


# Checks that the DV does not cause any of the IVs
# Issues a warning if dependent variable causes an independent variable
def check_design_dv(design: Design):
    dv = design.dv

    for i in design.ivs:
        dv_causes = design.graph.has_edge(start=dv, end=i, edge_type="cause")

        if dv_causes:
            raise ValueError(
                f"The dependent variable {dv.name} causes the independent variable {i.name}."
            )

# @returns a Python dict with all the effect options, can be used to output straight JSON or to write a file
# @param output_path is the file path to write out the data
def collect_model_candidates(query: Design, main_effects_candidates: Set[AbstractVariable], interaction_effects_candidates: Set[AbstractVariable], random_effects_candidates: Set[RandomEffect], family_link_paired_candidates: Dict[AbstractFamily, Set[AbstractLink]]):
    # Create dictionary 
    data = dict()
    data["input"] = dict()

    # Create query dict
    query_key = "query"
    data["input"][query_key] = dict()
    data["input"][query_key] = {"DV": query.dv.name, "IVs": [v.name for v in query.ivs]}

    # Create main effects dict 
    main_key = "generated main effects"
    data["input"][main_key] = list()
    data["input"][main_key] = [v.name for v in main_effects_candidates]

    # Create interaction effects dict
    interaction_key = "generated interaction effects"
    data["input"][interaction_key] = list()
    data["input"][interaction_key] = [v.name for v in interaction_effects_candidates]

    # Create random effects dict
    random_key = "generated random effects"
    data["input"][random_key] = dict()
    # Create expanded dicts
    # Group1: {random intercept: {groups: G}}
    # Group2: {random slope: {groups: G, iv: I}}
    # Group3: {random intercept: {groups: G}, random slope: {iv: I, groups: G}, correlated=True}
    tmp_random = dict()
    for r in random_effects_candidates: 
        if isinstance(r, RandomIntercept):
            tmp_random[r.groups.name]["random intercept"] = {"groups": r.groups}
        else: 
            assert(isinstance(r, RandomSlope))
            tmp_random[r.groups.name]["random slope"] = {"iv": r.iv, "groups": r.groups}

    # If there is a random intercept and slope involving the same grouping variable, add correlation value
    for key, value in tmp_random: 
        if len(value) == 2: 
            tmp_random["correlated"] = True
    
    data["input"][random_key] = tmp_random
    
    # Create family, link paired dict
    family_link_key = "generated family, link functions"
    data["input"][family_link_key] = dict()
    # {"Family 1": ["Link 1", "Link 2"]}, {"Family 2": ["Link 1", "Link 2"]}
    tmp_family_link = dict()
    for f, l_options in family_link_paired_candidates.items(): 
        import pdb; pdb.set_trace()
        f_classname = type(f).__name__
        tmp_family_link[f_classname] = [type(l).__name__ for l in l_options]
    data["input"][family_link_key] = tmp_family_link

    return data

# Write data to JSON file specified in @param output_path
def write_to_json(data: Dict, output_path: str, output_filename: str): 
    assert(output_filename.endswith(".json"))
    path = Path(output_path, output_filename)
    # Output dictionary to JSON
    with open(path, 'w+', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# @param file is the path to the JSON file from which to construct the statistical model
def construct_statistical_model(file: str, query: Design, main_effects_candidates: Set[AbstractVariable], interaction_effects_candidates: Set[AbstractVariable], random_effects_candidates: Set[RandomEffect], family_link_paired_candidates: Dict[AbstractFamily, Set[AbstractLink]]):
    pass

# @returns statistical model that reflects the study design
def infer_statistical_model_from_design(design: Design):
    gr = design.graph

    ### Step 1: Initial conceptual checks
    # Check that the IVs have a conceptual relationship (direct or transitive) with DV
    check_design_ivs(design)
    # Check that the DV does not cause one or more IVs
    check_design_dv(design)


    ### Step 2: Candidate statistical model inference/generation
    main_effects_candidates = infer_main_effects(gr=gr, query=design)
    # Assume all the main effects will be selected 
    main_effects_candidates = list(main_effects_candidates)
    
    interaction_effects_candidates = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects_candidates)
    interaction_effects_candidates = list(interaction_effects_candidates) 

    random_effects_candidates = infer_random_effects(gr=gr, query=design, main_effects=main_effects_candidates, interaction_effects=interaction_effects_candidates)

    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates: 
        # TODO: store the family-links somewhere!
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options 
        assert(f.__class__ not in family_link_paired.keys())
        family_link_paired[f.__class__] = l


    # Write out to JSON in order to pass data to Tisane GUI for disambiguation
    input_file = "input.json"
    data = collect_model_candidates(main_effects_candidates, interaction_effects_candidates, random_effects_candidates, family_link_paired, input_file)
    write_to_json(data, "input_file.json")
    # Note: Because the input to the GUI is a JSON file, everything is stringified. This means that we need to match up the variable names with the actual variable objects in the next step. 

    ### Step 3: Disambiguation loop (GUI)
    gui = TisaneGUI()
    gui.start_app(input=input_file)
    # Output a JSON file 
    output_file = "model_spec.json"

    # Read JSON file
    sm = None
    f = open(output_file, "r")

    ### Step 4: Code generation 
    # Construct StatisticalModel from JSON spec
    model_json = f.read()
    sm = construct_statistical_model(file=model_json, query=design, main_effects_candidates=main_effects_candidates, interaction_effects_candidates=interaction_effects_candidates, random_effects_candidates=random_effects_candidates, family_link_paired_candidates=family_link_paired).assign_data(
        design.dataset.dataset
    )
    # Generate code from SM
    script = generate_code(sm)

    return script