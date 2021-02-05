"""
SAMPLE PROGRAM
Input: Statistical model 
Output: Data procedure + data schema
"""

import tisane as ts

##### WITHOUT DATA #####
#stat_mod = ts.StatisticalModel(formula='SAT ~ Intelligence + Age')

# TODO: Step 0. Parse R formula input into instantiate StatisticalModel object

# Simple linear regression
stat_mod = ts.StatisticalModel( dv='SAT', 
                                main_effects=['Intelligence', 'Age'], 
                                interaction_effects=[], 
                                mixed_effects=[], 
                                link='identity', 
                                variance='normal') 

facts = stat_mod.to_logical_facts()

data_schema = stat_mod.query_data_schema()




# 2. store facts locally, not in separate file
# 3. query loop
# stat_md.find_data_collection_procedure()

# Idea
# stat_mod.find_data_schema().filter(...)



"""
# All IVs in one list
stat_mod = ts.StatisticalModel( dv_name='SAT', 
                                ivs_names=['Intelligence', 'Age'], 
                                link='identity', 
                                variance='normal') 

# IVs split up 
stat_mod = ts.StatisticalModel( dv='SAT', 
                                main_effects=['Intelligence', 'Age'], 
                                interaction_effects = [], 
                                mixed_effects = [],
                                link='identity', 
                                variance='normal') 
"""

# GOAL: set up so that know what user writes to get to knowledge base query..


# TODO: Question: How do we elicit info about link and variance functions? 

# TODO: What about use case where end-user starts with a formula but then doesnt know the link or variance functions? 



# TODO: Open question: What are we going to do about categorical variables and their encoding? 


# TODO: tests 
"""
# trying to output constraints to debug dynamic generation. 
        # not working:
        with('sample_test.lp', 'w') as outfile: 
            for l in KB.__effects_sets_to_constraints__[f'(ivs:{ivs}, dv:{[self.dv]})']:
                outfile.write("%s\n" % l)
"""