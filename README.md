
# About
An experiment to extend the functionality of the python fabric library (fabric3, the python 3 fork, to be exact).


# Development
```
pip install --editable . 
```
Links our code into our venv, allowing us to modify the package further.
(As opposed to copying over the files)

We will not be including a block like so:
```
if __name__ == '__main__':
  # something here
  pass
```

This is because we'll rely on setuptools to install 1 binary per top-level
command.