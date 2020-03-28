from distutils.core import setup

import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='whigo',  # How you named your package folder (MyLib)
    packages=setuptools.find_packages(),  # Chose the same as "name"
    version='0.1',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='What the Hell Is Going On?',  # Give a short description about your library
    author='Ankit Arora',  # Type in your name
    author_email='ankitarora121@gmail.com',  # Type in your E-Mail
    url='https://github.com/quixote911/whigo',  # Provide either the link to your github or to your website
    keywords=['monitoring', 'metrics', 'measure'],  # Keywords that define your package best
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
