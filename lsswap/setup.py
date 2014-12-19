from setuptools import setup
setup(name='lsswap',
      version='0.2',
      py_modules=['lsswap'],
      url='https://github.com/sxd/sysadmin-tools',
      author='Jonathan Gonzalez V',
      author_email='jgonzalez@linets.cl',
      description='lsswap aim to show all the swap information on a GNU/Linux machine',
      scripts=['bin/lsswap'],
      install_requires=['PrettyTable'],
  )
