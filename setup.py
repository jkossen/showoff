import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "showoff",
    version = '0.3',
    author = "Jochem Kossen",
    author_email = "jochem@jkossen.nl",
    license="BSD",
    description="Webbased image gallery and photo directory management",
    keywords="photo web gallery",
    long_description=read('README.rst'),
    packages=["showoff"],
    install_requires=[
        'Flask==0.9',
        'Flask-WTF==0.8',
        'py-bcrypt==0.2',
        'PIL==1.1.7'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: BSD License",
    ],
)
