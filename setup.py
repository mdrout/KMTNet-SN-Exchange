from setuptools import setup

setup(name='ksnex',
      author=['Maria Drout', 'Curtis McCully'],
      author_email=['maria.drout@dunlap.utoronto.ca', 'cmccully@lco.global'],
      version=0.1,
      packages=['ksnex'],
      setup_requires=[],
      install_requires=['numpy', 'astropy','django'],
      tests_require=[]
      )
