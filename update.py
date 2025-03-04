import os
import sys

if os.name == "posix":  # Linux/macOS
    print("Linux detected. Passing check.")
    sys.exit(0)

elif os.name == "nt":  # Windows
    try:
        import win32com.client
        app = win32com.client.Dispatch("PowerPoint.Application")
        print("Success: PowerPoint is accessible.")
        app.Quit()
    except ImportError:
        print("Error: pywin32 is not installed. Install it using 'pip install pywin32'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unable to access PowerPoint. Details: {e}")
        sys.exit(1)
else:
    print("Unknown OS detected. Exiting.")
    sys.exit(1)

set HTTP_PROXY=http://your-proxy-server:port
set HTTPS_PROXY=https://your-proxy-server:port
