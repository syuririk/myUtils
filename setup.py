from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / "requirements.txt") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]


package_names = ["src"]
package_path = [n + ".*" for n in package_names]

setup(
    name="myUtils",
    version="0.1.0",
    packages=find_packages(include=package_names + package_path),
    include_package_data=True,
    install_requires=requirements,

    description="My utils",
    long_description=(here / "README.md").read_text(encoding="utf-8")
        if (here / "README.md").exists() else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)