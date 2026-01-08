from setuptools import find_packages, setup

setup(
    name='circuithelper',
    version='0.1.0',
    description='Advanced circuit management plugin for NetBox',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Digital Vortex LLC',
    author_email='info@digitalvortex.com',
    url='https://github.com/DigitalVortexLLC/circuithelper',
    install_requires=[
        'netbox>=4.5.0',
        'fastkml>=1.0.0',  # For KMZ parsing
        'lxml>=4.9.0',  # Required by fastkml
        'shapely>=2.0.0',  # For geospatial data
        'folium>=0.15.0',  # For interactive maps
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'circuithelper': [
            'templates/circuithelper/**/*.html',
            'static/circuithelper/**/*',
        ],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
)
