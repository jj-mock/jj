from setuptools import setup, find_packages

setup(
    name='jj',
    description='A simple testing tool for mocking HTTP responses',
    version='0.1.4',
    url='https://github.com/nikitanovosibirsk/jj',
    author='Nikita Tsvetkov',
    author_email='nikitanovosibirsk@yandex.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'Werkzeug==0.14.1',
        'requests==2.21.0',
        'requests-toolbelt==0.9.1'
    ]
)
