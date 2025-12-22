import AVFoundation
import Foundation
print("Checking camera authorization status...")
let status = AVCaptureDevice.authorizationStatus(for: .video)
switch status {
case .authorized:
    print("✅ Already Authorized")
case .denied:
    print("❌ Denied. Please reset using: tccutil reset Camera")
case .restricted:
    print("⚠️ Restricted")
case .notDetermined:
    print("❓ Not Determined. Requesting access now...")
    let semaphore = DispatchSemaphore(value: 0)
    AVCaptureDevice.requestAccess(for: .video) { granted in
        print(granted ? "✅ Access Granted!" : "❌ Access Denied.")
        semaphore.signal()
    }
    _ = semaphore.wait(timeout: .now() + 10)
@unknown default:
    print("Unknown status")
}
