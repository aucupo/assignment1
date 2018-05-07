**Git initialization**

**Create a new repository**

```
git clone https://git.geo.tuwien.ac.at/pfogliar/drawing-app.git
cd drawing-app
touch README.md
git add README.md
git commit -m "add README"
git push -u origin master
```

**Existing folder**

```
cd existing_folder
git init
git remote add origin https://git.geo.tuwien.ac.at/pfogliar/drawing-app.git
git add .
git commit -m "Initial commit"
git push -u origin master
```

**Existing Git repository**

```
cd existing_repo
git remote rename origin old-origin
git remote add origin https://git.geo.tuwien.ac.at/pfogliar/drawing-app.git
git push -u origin --all
git push -u origin --tags
```

**Necessary Packages (Use Anaconda or miniconda)**

**Create the environment**
If using full Anaconda use the graphical interface to create a python=3.6 environment called "drawing_app" with the following pagackes:

* numpy
* pyqt=4
* pyopengl

If using miniconda, from the command line issue these commands
```
create -n drawing_app python=3.6 
conda install --name drawing_app numpy
conda install --name drawing_app pyqt=4
conda install --name drawing_app pyopengl
```