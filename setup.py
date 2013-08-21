from setuptools import setup

setup(
        name='showoff',
        version='0.3'
        long_description=__doc__,
        packages=['showoff'],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'Flask==0.9',
            'Flask-WTF==0.8',
            'py-bcrypt==0.2',
            'PIL==1.1.7'
        ]
)
