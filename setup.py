from setuptools import setup, find_packages

setup(
    name='Macro Maker',
    version='1.0',
    packages=find_packages(),
    description='An efficient program to make image-based macros',
    author='N0kov',
    author_email='nokovk@proton.me',
    url='https://github.com/N0kov/Macro-Maker',
    install_requires=['inflect', 'mss', 'numpy', 'pillow', 'pynput', 'PyQt6', 'word2number'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'macro_maker=UI3:main',
        ],
    },
)
