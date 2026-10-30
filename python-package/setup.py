from setuptools import find_packages, setup

setup(
    name="employee_events",
    version="0.1.0",
    description="SQL query API for the employee_events database",
    packages=find_packages(),
    package_data={"employee_events": ["*.db"]},
    include_package_data=True,
    install_requires=["pandas"],
    python_requires=">=3.9",
)
