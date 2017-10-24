from setuptools import setup

setup(name='web',
      version='1.0',
      description='OpenShift App',
      author='Your Name',
      author_email='example@example.com',
      url='https://www.python.org/community/sigs/current/distutils-sig',
      install_requires=['Flask>=0.7.2', 'requests','lxml==3.4.4','Pillow == 4.0.0', 'Flask-SQLAlchemy', 'Flask-Security==1.7.5'],
      )
