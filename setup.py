from setuptools import setup

setup(
    name='django-embedly',
    version='0.2',
    description='Provides a template filter and cached view to parse embed URLs and talk to embedly API',
    author='Josh Levinger, Bay Citizen',
    author_email='josh.l@engagementlab.org, info@baycitizen.org',
    url='http://github.com/jlev/django-embedly/',
    packages=[
        'embeds',
    ],

    install_requires=[
        'distribute',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
