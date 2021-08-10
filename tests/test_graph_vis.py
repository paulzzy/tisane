from tisane import graph
import tisane as ts
from tisane.variable import Has
from tisane.smt.synthesizer import Synthesizer

import unittest


class GraphVisTest(unittest.TestCase):
    # def test_vis(self):
    #     v1 = ts.Nominal("V1")
    #     v2 = ts.Nominal("V2")
    #     v3 = ts.Nominal("V3")
    #
    #
    #
    #     gr = ts.Graph()
    #     gr._add_variable(v1)
    #     gr._add_variable(v2)
    #     gr.causes(v1, v3)
    #     gr.causes(v2, v3)
    #
    #     gr.visualize_graph
    #     self.assertIsInstance(v1, ts.Nominal)
    # def test_units(self):
    #     student = ts.Unit("student id")
    #     school = ts.Unit("school id")
    #     test_score = student.numeric("test score")

    #     gr = ts.Graph()
    #     gr._add_variable(student)
    #     gr._add_variable(school)
    #     gr._add_variable(test_score)
    #     school.causes(test_score)
    #     # gr.has(student, test_score)
    #     gr.causes(school, test_score)
    #     gr.associates_with(student, test_score)

    #     gr._get_graph_tikz()

    #     # gr.visualize_graph()

    # def test_more_complex(self):

    #     student = ts.Unit(
    #         "Student", attributes=[]
    #     )  # object type, specify data types through object type
    #     race = student.nominal("Race", cardinality=5, exactly=1)  # proper OOP
    #     ses = student.numeric("SES")
    #     test_score = student.nominal("Test score")
    #     tutoring = student.nominal("treatment")

    #     race.associates_with(test_score)
    #     student.associates_with(test_score)
    #     race.causes(tutoring)

    #     race.moderates(ses, on=test_score)

    #     design = ts.Design(dv=test_score, ivs=[race, ses])
    #     print(design.get_variables())

    #     gr = design.graph
    #     print(gr.get_nodes())
    #     gr._get_graph_tikz()
    #     # self.assertTrue(gr.has_variable(test_score))
    #     gr.visualize_graph()

    # As of August 10, this is the example used in the README
    def test_exercise_group_simplified(self):
        adult = ts.Unit("member", cardinality=386)
        motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])
        # Adults have pounds lost. 
        pounds_lost = adult.numeric("pounds_lost")
        age = adult.numeric("age")
        # Adults have one of four racial identities in this study. 
        race = adult.nominal("race group", cardinality=4)
        week = ts.SetUp("Week", order=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        motivation_level.causes(pounds_lost)
        race.associates_with(pounds_lost)
        week.associates_with(pounds_lost)

        age.moderates(moderator=[motivation_level], on=pounds_lost)

        design = ts.Design(dv=pounds_lost, ivs=[age, race, week])
        gr = design.graph
        gr._get_graph_tikz()

#         \begin{tikzpicture}[cause/.style={draw=red, "c", text=red},
#                     associate/.style={draw=black},
#                     min/.style={minimum size=2cm},
#                     unit/.style={min,draw=black},
#                     measure/.style={min,circle,draw=black}]

#     \graph[spring layout,sibling distance=3cm,level distance=3cm]{
# 		member[unit] -> [has] pounds_lost[measure];
# 		member -> [has] age[measure];
# 		member -> [has] age*motivation[measure];
# 		member -> [has] race group[measure];
# 		pounds_lost -> [associates] race group;
# 		pounds_lost -> [associates] Week[measure];
# 		pounds_lost -> [associates] age*motivation;
# 		motivation[measure] -> [causes] pounds_lost;
# 		race group -> [associates] pounds_lost;
# 		Week -> [associates] pounds_lost;
# 		age*motivation -> [associates] pounds_lost;

#     };
# \end{tikzpicture}