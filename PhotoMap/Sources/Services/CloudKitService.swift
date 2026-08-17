import CloudKit
import CoreLocation
import UIKit

/// Manages a single shared CloudKit record zone ("SharedAlbum") used as the couple's
/// joint photo pool. One participant owns the zone (private database); the other
/// accesses the same zone through their shared database after accepting the CKShare.
@MainActor
final class CloudKitService: ObservableObject {
    static let containerIdentifier = "iCloud.com.reizen.photomap"
    static let zoneName = "SharedAlbum"
    static let photoRecordType = "Photo"

    private let container: CKContainer
    private let privateDB: CKDatabase
    private let sharedDB: CKDatabase

    @Published var accountStatus: CKAccountStatus = .couldNotDetermine
    @Published var isSharedZoneReady = false
    @Published var isZoneOwner = false
    @Published var photos: [PhotoPin] = []
    @Published var errorMessage: String?

    private var activeZoneID: CKRecordZone.ID?
    private var activeDatabase: CKDatabase?

    init() {
        container = CKContainer(identifier: Self.containerIdentifier)
        privateDB = container.privateCloudDatabase
        sharedDB = container.sharedCloudDatabase
    }

    func refreshAccountStatus() async {
        do {
            accountStatus = try await container.accountStatus()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    /// Looks for the shared zone, first as owner (private DB), then as an invited
    /// participant (shared DB). Call after login and after accepting a share.
    func locateAlbum() async {
        if let zones = try? await privateDB.allRecordZones(),
           let zone = zones.first(where: { $0.zoneID.zoneName == Self.zoneName }) {
            activeZoneID = zone.zoneID
            activeDatabase = privateDB
            isZoneOwner = true
            isSharedZoneReady = true
            await fetchPhotos()
            return
        }

        if let zones = try? await sharedDB.allRecordZones(),
           let zone = zones.first(where: { $0.zoneID.zoneName == Self.zoneName }) {
            activeZoneID = zone.zoneID
            activeDatabase = sharedDB
            isZoneOwner = false
            isSharedZoneReady = true
            await fetchPhotos()
            return
        }

        isSharedZoneReady = false
    }

    /// Owner-only: creates the custom zone that will hold the shared photos.
    func createSharedAlbum() async {
        let zone = CKRecordZone(zoneName: Self.zoneName)
        do {
            let saved = try await privateDB.save(zone)
            activeZoneID = saved.zoneID
            activeDatabase = privateDB
            isZoneOwner = true
            isSharedZoneReady = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    /// Owner-only: creates (or re-fetches) the CKShare for the album zone so it can be
    /// presented via `UICloudSharingController` to invite the partner.
    func makeShare() async -> CKShare? {
        guard isZoneOwner, let zoneID = activeZoneID else { return nil }

        if let existing = try? await fetchExistingShare(for: zoneID) {
            return existing
        }

        let share = CKShare(recordZoneID: zoneID)
        share[CKShare.SystemFieldKey.title] = "我们的相册" as CKRecordValue

        do {
            let zone = CKRecordZone(zoneID: zoneID)
            let result = try await privateDB.modifyRecords(saving: [zone, share], deleting: [])
            for (_, saveResult) in result.saveResults {
                if case .success(let record) = saveResult, let savedShare = record as? CKShare {
                    return savedShare
                }
            }
            return share
        } catch {
            errorMessage = error.localizedDescription
            return nil
        }
    }

    private func fetchExistingShare(for zoneID: CKRecordZone.ID) async throws -> CKShare? {
        let zone = try await privateDB.recordZone(for: zoneID)
        guard let shareID = zone.share?.recordID else { return nil }
        return try await privateDB.record(for: shareID) as? CKShare
    }

    /// Accepts an invitation the partner opened from the share link/AirDrop/Messages.
    func acceptShare(metadata: CKShare.Metadata) async {
        let op = CKAcceptSharesOperation(shareMetadatas: [metadata])
        do {
            try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
                op.acceptSharesResultBlock = { result in
                    switch result {
                    case .success:
                        continuation.resume()
                    case .failure(let error):
                        continuation.resume(throwing: error)
                    }
                }
                container.add(op)
            }
            await locateAlbum()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func fetchPhotos() async {
        guard let db = activeDatabase, let zoneID = activeZoneID else { return }
        let query = CKQuery(recordType: Self.photoRecordType, predicate: NSPredicate(value: true))
        query.sortDescriptors = [NSSortDescriptor(key: "timestamp", ascending: true)]

        do {
            let (matchResults, _) = try await db.records(matching: query, inZoneWith: zoneID)
            let records = matchResults.compactMap { try? $0.1.get() }
            photos = records.compactMap { PhotoPin(record: $0) }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func uploadPhoto(image: UIImage, coordinate: CLLocationCoordinate2D, timestamp: Date, ownerName: String) async {
        guard let db = activeDatabase, let zoneID = activeZoneID else {
            errorMessage = "相册还没准备好"
            return
        }
        guard let data = image.jpegData(compressionQuality: 0.8) else { return }

        let tmpURL = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".jpg")
        do {
            try data.write(to: tmpURL)
            let record = CKRecord(recordType: Self.photoRecordType, recordID: CKRecord.ID(zoneID: zoneID))
            record["asset"] = CKAsset(fileURL: tmpURL)
            record["latitude"] = coordinate.latitude
            record["longitude"] = coordinate.longitude
            record["timestamp"] = timestamp
            record["ownerName"] = ownerName

            _ = try await db.save(record)
            try? FileManager.default.removeItem(at: tmpURL)
            await fetchPhotos()
        } catch {
            errorMessage = error.localizedDescription
            try? FileManager.default.removeItem(at: tmpURL)
        }
    }
}
