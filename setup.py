from setuptools import setup, find_packages
from setuptools.command.install import install as SetuptoolsInstall
import subprocess, os, sys

# EMopt depends on the PETSc and SLEPc libraries. These can be installed through pip
# however not quite automatically. Here, we manually pip install the petsc and slepc
# packages in required way.
try:
    import petsc4py
except:
    if('PETSC_DIR' not in os.environ or 'PETSC_ARCH' not in os.environ):
        os.environ['PETSC_CONFIGURE_OPTIONS'] = "--with-scalar-type=complex " \
                                                            "--with-mpi=1 " \
                                                            "--COPTFLAGS='-O3' " \
                                                            "--FOPTFLAGS='-O3' " \
                                                            "--CXXOPTFLAGS='-O3' " \
                                                            "--with-debugging=0 " \
                                                            "--download-scalapack " \
                                                            "--download-mumps " \
                                                            "--download-openblas"
        if('numpy' not in sys.modules):
            subprocess.call(['pip3', 'install', 'numpy'])

        subprocess.call(['pip3', 'install', 'petsc', 'petsc4py', '--no-binary', ':all:'])

try:
    import slepc4py
except:
    if('SLEPC_DIR' not in os.environ):
        subprocess.call(['pip3', 'install', 'slepc', 'slepc4py', '--no-binary', ':all:'])


class MakeInstall(SetuptoolsInstall):
    # Add a commandline argument for emopt prefix
    user_options = SetuptoolsInstall.user_options + [('emopt-prefix=', None, None)]

    def initialize_options(self):
        SetuptoolsInstall.initialize_options(self)
        self.emopt_prefix = None

    def finalize_options(self):
        SetuptoolsInstall.finalize_options(self)

    def run(self):
        # Compile C++ components of EMopt
        subprocess.call('make')
        SetuptoolsInstall.do_egg_install(self)

def get_version_number():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    with open(base_dir + '/emopt/__init__.py', 'r') as fin:
        for line in fin:
            if('__version__' in line):
                version = line.split('=')[-1].strip().strip().strip('\"')

    return version

setup(name='emopt',
      version=get_version_number(),
      description='A suite of tools for optimizing the shape and topology of ' \
      'electromagnetic structures.',
      url='https://github.com/anstmichaels/emopt',
      author='Andrew Michaels',
      author_email='amichaels@berkeley.edu',
      license='GPL 3.0',
      packages=find_packages(),
      package_data={'emopt':['*.so', '*.csv', 'data/*', 'solvers/*.so']},
      cmdclass={'install':MakeInstall},
      install_requires=['numpy', 'scipy', 'matplotlib', 'mpi4py', 'petsc4py', 'slepc4py'],
      zip_safe=False)
