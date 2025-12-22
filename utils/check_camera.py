import platform
import os
import subprocess

def check_mac_camera():
    import ctypes
    import ctypes.util
    try:
        # Load AVFoundation and Foundation frameworks
        objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
        avf = ctypes.cdll.LoadLibrary(ctypes.util.find_library('AVFoundation'))
        foundation = ctypes.cdll.LoadLibrary(ctypes.util.find_library('Foundation'))

        # Define necessary types
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.objc_msgSend.restype = ctypes.c_void_p
        objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        # Helper to send messages
        def msg(obj, sel_name, *args, restype=ctypes.c_void_p, argtypes=None):
            sel = objc.sel_registerName(sel_name.encode('ascii'))
            f = objc.objc_msgSend
            f.restype = restype
            if argtypes:
                f.argtypes = [ctypes.c_void_p, ctypes.c_void_p] + argtypes
            else:
                f.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            return f(obj, sel, *args)

        # Get AVCaptureDevice class
        AVCaptureDevice = objc.objc_getClass(b'AVCaptureDevice')
        ns_string_class = objc.objc_getClass(b'NSString')
        
        def to_ns_string(s):
            return msg(ns_string_class, 'stringWithUTF8String:', ctypes.c_char_p(s.encode('utf-8')), argtypes=[ctypes.c_char_p])

        AVMediaTypeVideo = to_ns_string('vide')

        # Check Authorization Status
        status = msg(AVCaptureDevice, 'authorizationStatusForMediaType:', AVMediaTypeVideo, restype=ctypes.c_long, argtypes=[ctypes.c_void_p])
        
        status_map = {0: "Not Determined", 1: "Restricted", 2: "Denied", 3: "Authorized"}
        print(f"Current macOS Camera Authorization Status: {status_map.get(status, 'Unknown')} ({status})")
        
        if status == 0:
            print("Attempting to trigger authorization prompt...")
            device = msg(AVCaptureDevice, 'defaultDeviceWithMediaType:', AVMediaTypeVideo, argtypes=[ctypes.c_void_p])
            if device:
                print("Got default device. If no prompt appeared, try running the app.")
            else:
                print("Could not find a camera device.")
        
        print("\nTo manually fix this on macOS:")
        print("1. Go to System Settings > Privacy & Security > Camera")
        print("2. Ensure Terminal (or VS Code) is enabled.")
        
    except Exception as e:
        print(f"Error checking macOS camera: {e}")

def check_windows_camera():
    print("Checking camera on Windows...")
    print("Note: Windows doesn't require complex API calls for basic permission checks in the same way macOS does.")
    print("If the camera is not working:")
    print("1. Go to Settings > Privacy & security > Camera")
    print("2. Ensure 'Camera access' is On.")
    print("3. Ensure 'Let desktop apps access your camera' is On.")
    
    try:
        import cv2
        print("\nTesting camera access using OpenCV...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Successfully opened camera 0.")
            cap.release()
        else:
            print("❌ Failed to open camera 0.")
    except ImportError:
        print("\nOpenCV not installed. Cannot test opening camera directly.")
        print("Try: pip install opencv-python")

def check_linux_camera():
    print("Checking camera on Linux...")
    devices = [f for f in os.listdir('/dev') if f.startswith('video')]
    if not devices:
        print("❌ No camera devices found in /dev/video*")
    else:
        print(f"Found devices: {', '.join(devices)}")
        for dev in devices:
            dev_path = f"/dev/{dev}"
            if os.access(dev_path, os.R_OK | os.W_OK):
                print(f"✅ Permissions OK for {dev_path}")
            else:
                print(f"❌ No R/W permissions for {dev_path}")
        
        # Check group membership
        try:
            user = os.getlogin()
            groups = subprocess.check_output(['groups', user]).decode()
            if 'video' in groups:
                print(f"✅ User '{user}' is in the 'video' group.")
            else:
                print(f"⚠️ User '{user}' is NOT in the 'video' group. You might need to run: sudo usermod -aG video {user}")
        except Exception:
            pass

    try:
        import cv2
        print("\nTesting camera access using OpenCV...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Successfully opened camera 0.")
            cap.release()
        else:
            print("❌ Failed to open camera 0.")
    except ImportError:
        print("\nOpenCV not installed. Try: pip install opencv-python")

if __name__ == "__main__":
    system = platform.system()
    if system == "Darwin":
        check_mac_camera()
    elif system == "Windows":
        check_windows_camera()
    elif system == "Linux":
        check_linux_camera()
    else:
        print(f"Camera check not explicitly implemented for {system}.")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            print(f"Camera 0 is {'Open' if cap.isOpened() else 'Closed'}")
            cap.release()
        except ImportError:
            print("OpenCV not installed.")
