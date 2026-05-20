import sys

checks={
    "tkinter": lambda: __import__("tkinter").__version__,
    "numpy": lambda: __import__("numpy").__version__,
    "pandas": lambda: __import__("pandas").__version__,
    "matplotlib": lambda: __import__("matplotlib").__version__,
    "markdown": lambda: __import__("markdown").__version__,
    "ipykernel": lambda: __import__("ipykernel").__version__,
    "serial": lambda: __import__("serial").__version__,
    "flask": lambda: __import__("flask").__version__,
    "requests": lambda: __import__("requests").__version__,
    "sseclient-py": lambda: __import__("sseclient-py").__version__,
}

GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"
failed=[]

for pkg, ver in checks.items():
    try:
        print(f"{GREEN}{pkg:<20} {ver}{RESET}")
    except Exception as e:
        print(f"{RED}{pkg:<20} not found{RESET}")
        failed.append(pkg)

if failed:
    print(f"\n{RED}The following packages are missing: {', '.join(failed)}{RESET}")
    sys.exit(1)
else:
    print(f"\n{GREEN}All packages are installed!{RESET}")