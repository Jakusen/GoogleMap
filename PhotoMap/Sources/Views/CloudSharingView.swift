import SwiftUI
import CloudKit
import UIKit

/// Wraps `UICloudSharingController` so the album owner can invite their partner
/// via Messages/AirDrop/Mail using the system share sheet.
struct CloudSharingView: UIViewControllerRepresentable {
    let share: CKShare
    let container: CKContainer

    func makeUIViewController(context: Context) -> UICloudSharingController {
        share[CKShare.SystemFieldKey.title] = share[CKShare.SystemFieldKey.title] ?? ("我们的相册" as CKRecordValue)
        let controller = UICloudSharingController(share: share, container: container)
        controller.availablePermissions = [.allowReadWrite, .allowPrivate]
        return controller
    }

    func updateUIViewController(_ uiViewController: UICloudSharingController, context: Context) {}
}
