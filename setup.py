from setuptools import setup, find_packages

setup(
    name='genshin-artifact-scanner',
    version='0.0.1',
    author='xloc',
    author_email='xloc.cc@outlook.com',
    description='An artifact parser from the artifact listing pages to a list of artifact attributes for the game Genshin Impact',
    packages=find_packages(),
    py_modules=['sketch'],
)