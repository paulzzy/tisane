from tisane.variable import AbstractVariable
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.synthesizer import Synthesizer
from tisane.helpers import *

from typing import List, Any
import subprocess
from subprocess import DEVNULL
import os
import sys

import plotly.figure_factory as ff
import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import webbrowser # For autoamtically opening the browser for the CLI

external_stylesheets = [dbc.themes.BOOTSTRAP]
port = '8050' # default dash port
def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

        
class InputInterface(object): 
    design: Design 
    statistical_model: StatisticalModel
    app: dash.Dash

    def __init__(self, design: Design, synthesizer: Synthesizer):
        self.design = design
        self.synthesizer = synthesizer
        
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        main_heading = html.H1(children='Main Effects')
        main_effects = self.populate_main_effects()
        main_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "Save and lock main effects", "value": False}
                    ],
                    value=[],
                    id='main_effects_switch',
                    switch=True,
                ),
            ],
            id='main_effects_group'
        )

        interaction_heading = html.H1(children='Interaction Effects')
        interaction_effects = self.populate_interaction_effects()
        interaction_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "Save and lock interaction effects", "value": False}
                    ],
                    value=[],
                    id='interaction_effects_switch',
                    switch=True,
                ),
            ],
            id='interaction_effects_group'
        )

        random_heading = html.H1(children='Random Effects')
        random_effects = self.populate_random_effects()
        random_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "Save and lock random effects", "value": False}
                    ],
                    value=[],
                    id='random_effects_switch',
                    switch=True,
                ),
            ],
            id='random_effects_group'
        )

        family_heading = html.H1(children='Family Distribution')
        # data_dist = self.draw_data_dist()
        family_dist_div = self.populate_compound_family_div()
        # family_options = self.populate_data_distributions()

        
        # TODO: Layout Main | Interaction in a visually appealing way
        
        # Create Dash App
        app.layout = dbc.Container([
            # html.Div([main_heading, main_switch]),
            main_heading, 
            main_switch,
            main_effects,
            # html.Div([interaction_heading, interaction_switch]),
            interaction_heading,
            interaction_switch,
            interaction_effects,
            random_heading,
            random_switch,
            random_effects,
            family_heading, 
            family_dist_div,
            # family_options
        ])
        
        @app.callback(
            Output('main_effects_options', 'options'),
            [Input('main_effects_switch', 'value'),
            State('main_effects_options', 'options')],
            # State('main_effects_options', 'options')
        )
        def save_main_effects(switch_value, main_effects_options):
            output = list()
            if switch_value: 
                facts = list()
                for o in main_effects_options: 
                    facts.append(o['value'])
                    output.append({'label': o['label'], 'value': o['value'], 'disabled': True})
                    
                is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
                if is_sat: 
                    self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
                    return output
                else: 
                    # TODO: Start a modal?
                    raise ValueError(f"Error in saving main effects!")
            else: 
                for o in main_effects_options: 
                    output.append({'label': o['label'], 'value': o['value'], 'disabled': False})
                
                return output
        
        @app.callback(
            Output('two-way_options', 'labelStyle'),
            Output('n-way_options', 'labelStyle'),
            [Input('interaction_effects_switch', 'value'),
            Input('two-way_options', 'options'),
            Input('n-way_options', 'options')]
        )
        def save_interaction_effects(two_way_options, n_way_options, switch_val):
            if switch_val == 'save': 
                facts = list()

                for o in two_way_options: 
                    facts.append(two_way_options['value'])
                
                for o in n_way_options: 
                    facts.append(two_way_options['value'])
                
                is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
                # return html.Div(f"{is_sat}")
                if is_sat: 
                    self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
                    # TODO: Lock the interaction effects options
                    return {'disabled': True}
                else: 
                    # TODO: Start a modal?
                    raise ValueError(f"Error in saving main effects!")
            else: 
                raise PreventUpdate
                
        @app.callback(
            [Output(f"{i}_collapse", "is_open") for i in ['two-way', 'n-way']],
            [Input(f"{i}_toggle", "n_clicks") for i in ['two-way', 'n-way']],
            [State(f"{i}_collapse", "is_open") for i in ['two-way', 'n-way']],
        )
        def toggle_accordion(n1, n2, is_open1, is_open2):
            ctx = dash.callback_context

            if not ctx.triggered:
                return False, False
            else:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == "two-way_toggle" and n1:
                return not is_open1, False
            elif button_id == "n-way_toggle" and n2:
                return False, not is_open2
            return False, False

        # # Get rules 
                # rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

                # # Solve constraints + rules
                # (res_model_fixed, res_facts_fixed) = QM.solve(facts=fixed_facts, rules=rules_dict)
                
                # # Update result StatisticalModel based on user selection 
                # sm = QM.postprocess_to_statistical_model(model=res_model_fixed, facts=res_facts_fixed, graph=design.graph, statistical_model=sm)

                # # Design 1
                # # main_effects = from synth
                # # conflicts = from synth
                # # update div based on conflict 
                # # Callback where div selection "resolves conflict"
                # # Then lock the choice.

                # # Design 2
                # # better design -> temporary storage with user selected choices. Then at the end update/check for SAT
                # # Suggestions just get "*based on your conceptual model, ...." recommendation tag?
                
                # # App contains all the relationships...(visually show the conceptual relationships? under: show the measurement relationships)
        
        open_browser()
        app.run_server(debug=False, threaded=True)
        
        self.app = app
    
    def populate_main_effects(self): 
        output = list()
        # Get possible main effects from synthesizer
        possible_main_effects = self.synthesizer.generate_main_effects(design=self.design)

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay them out
        variable_options = list()
        for (variable, facts) in possible_main_effects.items(): 
            variable_options.append({'label': str(variable), 'value': f'{facts[0]}'})
        output = dbc.FormGroup([
            dbc.Checklist(
                options=variable_options,
                value=[],
                id="main_effects_options",
            ),
        ])

        return output

    def populate_interaction_effects(self): 
        output = list()
        # Get possible main effects from synthesizer
        possible_interaction_effects = self.synthesizer.generate_interaction_effects(design=self.design)

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay them out
        for (num_interactions, options) in possible_interaction_effects.items(): 
            interaction_options = list()
            for (name, fact) in options.items():
                interaction_options.append({'label': name, 'value': str(fact)})
            
            output.append(self.make_interaction_card(title=num_interactions, options=interaction_options))
            
        return html.Div(output, className='accordion')
    
    def populate_random_effects(self): 
        # Could be random slope OR random interaction 
        output = list()
        # Get possible main effects from synthesizer
        possible_random_effects = self.synthesizer.generate_random_effects(design=self.design)

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay them out
        for (key, facts) in possible_random_effects.items(): 
            output.append(self.make_random_checklist(label=key, options=facts))
            
            # TODO: correlate should only be an option if both are selected

        # return output
        return html.Div(output)
    
    def get_data_dist(self): 
        dv = self.design.dv
        
        data = self.design.get_data(variable=dv)
        
        if data is not None: 
            hist_data = [data]
            labels = [dv.name]
        else: 
            raise NotImplementedError
        
        return (hist_data, labels)

    def draw_dist(self, hist_data, labels): 
        fig = ff.create_distplot(hist_data, labels)

        fig_elt = dcc.Graph(figure=fig)

        return fig_elt
        
    def draw_data_dist(self): 
        (hist_data, labels) = self.get_data_dist()

        return self.draw_dist(hist_data, labels)

    def populate_data_distributions(self): 
        output = list() 

        (data, labels) = self.get_possible_family_distributions()

        # fig = px.histogram(family_data, x=f"{Value of self.design.dv.name}", y="frequency", color="dist", marginal="rug",
        #                 hover_data=df.columns)

        fig = ff.create_distplot(data, labels, showlegend=False)
        output.append(html.Div([
            html.H3(str(dist)),  
            dcc.Graph(figure=fig)
            ]))

        return html.Div(output)
    
    def get_possible_family_distributions(self): 
        dist_names = self.synthesizer.generate_family_distributions(design=self.design)

        data = list()
        labels = list()
        for dist in dist_names: 
            data.append(generate_data_dist_from_facts(fact=dist, design=self.design))
            labels.append(f'{self.design.dv.name} with {dist}')

        return (data, labels)        

    def populate_compound_family_div(self): 

        (curr_data_dist, curr_data_label) = self.get_data_dist()

        (possible_family_dists, possible_family_labels) = self.get_possible_family_distributions()

        # Combine data
        data = curr_data_dist + possible_family_dists
        labels = curr_data_label + possible_family_labels 

        fig = ff.create_distplot(data, labels)
        fig_div = html.Div([
            # html.H3(str(dist)),  
            dcc.Graph(figure=fig)
            ])

        return fig_div

    def populate_link_div(self): 
        (curr_data_dist, curr_data_label) = self.get_data_dist()

    # TODO: Need to add callbacks to this...
    def make_link_options(self): 
        dist_names = self.synthesizer.generate_family_distributions(design=self.design)

        link_functions = list()

        # Make a dict with 'family name': [link_functions]
        





    def make_interaction_card(self, title: str, options: List): 
        card = dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"{title}",
                        color="link",
                        id=f"{title}_toggle",
                    )
                )
            ),
            dbc.Collapse(
                dbc.FormGroup([
                    dbc.Checklist(
                        options=options,
                        value=[],
                        id=f"{title}_options",
                        labelStyle={'disabled': True}
                    ),
                ]),
                id=f'{title}_collapse'
            )
        ])
        return card

    def make_random_checklist(self, label: str, options: List): 
        checklist = dbc.FormGroup([
            dbc.Label(label),
            dbc.Checklist(
                options=[
                    {'label': 'Random slope', 'value': f'{options[0]}'},
                    {'label': 'Random intercept', 'value': f'{options[1]}'},
                    {'label': 'Correlated random slope & intercept', 'value': f'{options[2]}'}
                ],
                value=[],
                labelStyle={'display': 'inline-block'}
            )  
        ])
        return checklist
            # TODO: correlate should only be an option if both are selected

    
    @classmethod
    def ask_inclusion_prompt(cls, subject: str) -> bool: 

        prompt = f'Would you like to include {subject}?'
        choices = f' Y or N: '

        while True: 
            ans = add_inclusion_prompt(prompt=prompt, choices=choices)
            if ans.upper() == 'Y': 
                return ans.upper()
            elif ans.upper() == 'N': 
                return ans.upper()
            else: 
                pass
    
    @classmethod
    def ask_inclusion(cls, subject: str) -> bool: 
    
        ans = cls.ask_inclusion_prompt(subject)

        if ans.upper() == 'Y':
            # TODO: write to a file here 
            return True
        elif ans.upper() == 'N': 
            return False
        else: 
            pass
    
    # TODO: Format the interactions to be more readable
    @classmethod 
    def format_options(cls, options: List) -> List: 
        return options

    @classmethod
    def ask_multiple_choice_prompt(cls, options: List) -> Any: 
        prompt = f'These cannot be true simultaneously.'
        formatted_options = cls.format_options(options)
        choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '
        while True: 
            idx = int(input(prompt + choices))
            # st.write()

            if idx in range(len(options)): 
                # only keep the constraint that is selected. 
                constraint = options[idx] 
                print(f'Ok, going to add {constraint} and remove the others.')
                return idx
            else:
                print(f'Pick a value in range')
                pass
    
    @classmethod
    def resolve_unsat(cls, facts: List, unsat_core: List) -> List: 
        idx = cls.ask_multiple_choice_prompt(options=unsat_core)
    
        return unsat_core[idx]

    # TODO: Format options for specifying family of a distribution
    @classmethod
    def format_family(cls, options: List): 
        return options
    
    @classmethod
    def ask_family_prompt(cls, options: List, dv: AbstractVariable): 
        prompt = f'Which distribution best approximates your dependent variable {dv}?'
        formatted_options = cls.format_options(options)
        choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '

        while True: 
            idx = int(input(prompt + choices))

            if idx in range(len(options)): 
                # only keep the constraint that is selected. 
                constraint = options[idx] 
                print(f'Ok, going to add {constraint} and remove the others.')
                return idx
            else:
                print(f'Pick a value in range')
                pass
    
    @classmethod
    def ask_family(cls, options: List, dv: AbstractVariable): 
        idx = cls.ask_family_prompt(options=options, dv=dv)

        return options[idx]

    @classmethod
    def ask_link_prompt(cls, options: List, dv: AbstractVariable): 
        prompt = f'W'


    @classmethod
    def ask_link(cls, options: List, dv: AbstractVariable): 
        idx = cls.ask_link_prompt(options=options, dv=dv)

        return options[idx]

    # @classmethod
    # def ask_change_default_prompt(cls, subject: str, default: str, options: List): 
    #     prompt = f'The default {subject} is {default}. Would you like to change it to one of {options}?'

    # @classmethod
    # def ask_change_default(cls, subject: str, default: str, options: List): 
    #     idx = cls.ask_change_default_prompt(subject=subject, default=default, options=options)
    #     pass