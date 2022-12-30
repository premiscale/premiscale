# For reference ~ https://github.com/pypa/sampleproject/blob/main/setup.py

import pathlib

from setuptools import setup, find_packages

# Cf. https://github.com/dave-shawley/setupext-janitor#installation
try:
   from setupext_janitor import janitor
   cleanCommand = janitor.CleanCommand
except ImportError:
   cleanCommand = None

cmd_classes = {}
if cleanCommand is not None:
   cmd_classes['clean'] = cleanCommand


here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='autoscaler',
    version='0.0.1',
    description='Autoscaling for virtual machines over the libvirt API.',
    cmdclass=cmd_classes,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Emma Doyle',
    author_email='emma@premiscale.com',
    keywords='kvm, virtualization, virtual machine, vm, autoscaler, autoscaling, libvirt',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.10, <4',
    url = 'https://github.com/premiscale/autoscaler',
    install_requires=[],
    entry_points={
        "console_scripts": ["autoscale = cli.autoscaler:cli"]
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/premiscale/autoscaler/issues',
        'Source': 'https://github.com/premiscale/autoscaler'
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
