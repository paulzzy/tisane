# Tisane Tutorial
Welcome to Tisane, a data analysis tool that focuses on supporting conceptual
statistical relationships in study designs. After providing a study design
specification in the Tisane domain-specific language (DSL), the Tisane GUI
guides you through the process of generating an appropriate model. The resulting
model is written in Python, and you can run it to get results that answer your
research questions.

## Installation
Tisane requires Python 3.8+ and also an installation of R (see below).

First, install Tisane using `pip`:

```
pip install tisane
```

We recommend using a virtualenv with `pip` to keep your dependencies clean. Equivalently, you could also use [`poetry`](https://python-poetry.org), and add Tisane to your dependencies for your data analysis:

```
poetry add tisane
```

Second, you will need to install the R packages `lme4`, `lmerTest`, and `emmeans`.

```
install.packages(c('lme4','lmerTest','emmeans'))
```

(You can do this either by copying the above code into a file and running it using R, or you open an R shell and run the above line.)

### Installing R
For convenience, here are several ways you can install R:

#### Anaconda
[Anaconda](https://www.anaconda.com/distribution/) is a popular Python data science package manager, that can also be used to install R. This will also install the required R packages.

```
conda install -c conda-forge r r-base r-lmertest r-emmeans rpy2
```

#### Download it
Visit [this page](https://cran.r-project.org) and select the version for your operating system.

#### Download RStudio
RStudio is a popular IDE for developing R scripts. You can download it [here](https://www.rstudio.com/products/rstudio/).

## Using Tisane
Tisane is a tool for authoring generalized linear models. There are three stages to
authoring your model:

1. Writing the model specification in the Tisane DSL and producing a study design `tisane.Design`
2. Using `tisane.infer_statistical_model_from_design` on your study design, which examines your model and looks for additional variables you may want to add. Then, you can decide whether or not to use those variables, and also choose family and link functions, in a GUI that is launched. After making these additional choices, the GUI will generate a model script written in Python.
3. After running the script, the results of the model will be output so that you can examine them.

There are two different workflows for using Tisane.

### Using Tisane in a Jupyter Notebook

You can create your study design specification, launch the Tisane GUI, and run the model script all inside a Jupyter notebook!

This requires a couple of extra steps, but if you're used to running data analyses in Jupyter notebooks, Tisane will integrate all the more smoothly into
your data analysis workflow.

#### Setting up a Jupyter kernel

You will need to make sure that the jupyter notebook can find the dependencies you need, including Tisane and others.

##### With poetry
Make sure you have `ipykernel` added to your `poetry` dependencies, and then
create a kernel for ipython.

```
poetry add ipykernel
poetry run python -m ipykernel install --user --name <MY-KERNEL-NAME>
```

##### With pip and a virtual environment
Make sure you have your virtual environment, or venv, activated. Then run:

```
# install ipykernel
pip install ipykernel
# create the kernel, which is specific to the particualr venv
python -m ipykernel install --name <MY-KERNEL-NAME>
```

#### Opening the notebook
Once you've created your kernel, you can run `jupyter notebook`. Open up any notebook, and go to the menu: `Kernel > Change kernel`, and choose `<MY-KERNEL-NAME>` (whatever you called it) from the list. Then you should be good to go! After importing Tisane in your notebook, all three stages of using Tisane can be completed within the notebook itself.

### Using Tisane via the command line
With this workflow, you

1. Write your study design specification in the Tisane DSL in any IDE or plain old text editor of your choice. The last line in the file should be the call to `tisane.infer_statistical_model_from_design`
2. Run the python file from the command line. This should look like `python3 <my-tisane-design-file>.py` or `poetry run python3 <my-tisane-design-file>.py`. This will open up the Tisane GUI.
3. After generating code in the Tisane GUI, you will get the path to the output model. You can copy it, and then go back to the command line and run `python3 <copied-path-goes-here>` or `poetry run python3 <copied-path-goes-here>`

This way, you get to use whatever IDE you like to write the specification using the Tisane DSL.