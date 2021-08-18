from tisane.gui.gui import TisaneGUI
import os


# @param input is a json file that has all the data to read in
def start_gui(input: str):
    gui = TisaneGUI()

    gui.start_app(input)

class ExampleData:
    main_only_input=os.path.join(os.path.dirname(__file__),"example_inputs/main_only.json")
    # TODO: Add more input sources and json files here

start_gui(ExampleData.main_only_input)
