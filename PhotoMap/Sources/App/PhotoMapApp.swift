import SwiftUI
import CloudKit
import UIKit

/// Bridges the UIKit-only `userDidAcceptCloudKitShareWith` callback (fired when the
/// partner taps a shared-album invitation link) into the SwiftUI CloudKitService.
final class AppDelegate: NSObject, UIApplicationDelegate {
    var cloudKitService: CloudKitService?

    func application(_ application: UIApplication, userDidAcceptCloudKitShareWith cloudKitShareMetadata: CKShare.Metadata) {
        Task { @MainActor in
            await cloudKitService?.acceptShare(metadata: cloudKitShareMetadata)
        }
    }
}

@main
struct PhotoMapApp: App {
    @StateObject private var cloudKitService = CloudKitService()
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(cloudKitService)
                .onAppear {
                    appDelegate.cloudKitService = cloudKitService
                }
        }
    }
}
