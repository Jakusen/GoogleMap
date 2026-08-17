import CloudKit
import CoreLocation

struct PhotoPin: Identifiable, Hashable {
    let id: CKRecord.ID
    let assetURL: URL?
    let coordinate: CLLocationCoordinate2D
    let timestamp: Date
    let ownerName: String

    init?(record: CKRecord) {
        guard
            let latitude = record["latitude"] as? Double,
            let longitude = record["longitude"] as? Double,
            let timestamp = record["timestamp"] as? Date
        else { return nil }

        self.id = record.recordID
        self.coordinate = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        self.timestamp = timestamp
        self.ownerName = record["ownerName"] as? String ?? "未知"

        if let asset = record["asset"] as? CKAsset {
            self.assetURL = asset.fileURL
        } else {
            self.assetURL = nil
        }
    }

    static func == (lhs: PhotoPin, rhs: PhotoPin) -> Bool {
        lhs.id == rhs.id
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}
