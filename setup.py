from setuptools import setup

setup(
    name="ratecurve",
    version="0.0.4",
    description="""simple utility for curve interpolation""",
    author="Disent",
    author_email="chris@disent.com",
    license="Apache Software License",
    url="https://github.com/disentcorp/ratecurve",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Utilities",
        "Operating System :: Unix",
    ],
    packages=[
        "ratecurve",
    ],
    include_package_data=True,
    install_requires=["numpy","pandas","scipy","dateroll"],
    license_files=("LICENSE",),
    python_requires=">=3.10",
    zip_safe=False,
)
