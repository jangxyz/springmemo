from distutils.core import setup
setup(name='pymock',
      version='1.0.4',
      author='Jeff Younker',
      author_email='jeff@theblobshop.com',
      maintainer_email='jeff@theblobshop.com',
      url='http://www.theblobshop.com',
      py_modules=['pymock'],
      package_dir={'': 'lib'},
      packages=['pymock', 'test', 'test.pymock']
      )

