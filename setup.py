from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# requirements.txt 읽기
req_path = here / "requirements.txt"
requirements = []
if req_path.exists():
    with open(req_path, encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="myUtils",
    version="0.1.6",
    
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    description="My utils",
    long_description=(here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else "",
    long_description_content_type="text/markdown",
)