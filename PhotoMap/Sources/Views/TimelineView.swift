import SwiftUI

struct TimelineView: View {
    @EnvironmentObject var cloudKitService: CloudKitService
    @AppStorage("displayName") private var displayName: String = "我"
    @State private var filter: AlbumFilter = .all

    private var filteredPhotos: [PhotoPin] {
        cloudKitService.photos
            .filter(matchesFilter)
            .sorted { $0.timestamp > $1.timestamp }
    }

    private var dayGroups: [(day: String, photos: [PhotoPin])] {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy年M月d日"
        var order: [String] = []
        var buckets: [String: [PhotoPin]] = [:]
        for photo in filteredPhotos {
            let key = formatter.string(from: photo.timestamp)
            if buckets[key] == nil {
                buckets[key] = []
                order.append(key)
            }
            buckets[key]?.append(photo)
        }
        return order.map { (day: $0, photos: buckets[$0] ?? []) }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Picker("筛选", selection: $filter) {
                        ForEach(AlbumFilter.allCases) { Text($0.rawValue).tag($0) }
                    }
                    .pickerStyle(.segmented)
                }
                .listRowSeparator(.hidden)

                ForEach(dayGroups, id: \.day) { group in
                    Section(group.day) {
                        ForEach(group.photos) { photo in
                            TimelineRow(photo: photo)
                        }
                    }
                }
            }
            .navigationTitle("时间轴")
            .refreshable { await cloudKitService.fetchPhotos() }
            .overlay {
                if filteredPhotos.isEmpty {
                    ContentUnavailableView("还没有照片", systemImage: "photo.on.rectangle.angled")
                }
            }
        }
    }

    private func matchesFilter(_ photo: PhotoPin) -> Bool {
        switch filter {
        case .all: return true
        case .mine: return photo.ownerName == displayName
        case .partner: return photo.ownerName != displayName
        }
    }
}

private struct TimelineRow: View {
    let photo: PhotoPin

    private var timeText: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: photo.timestamp)
    }

    var body: some View {
        HStack(spacing: 12) {
            AsyncPhotoThumbnail(url: photo.assetURL)
                .frame(width: 64, height: 64)
                .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(photo.ownerName).font(.subheadline.bold())
                Text(timeText).font(.caption).foregroundStyle(.secondary)
                Text(String(format: "%.4f, %.4f", photo.coordinate.latitude, photo.coordinate.longitude))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

struct AsyncPhotoThumbnail: View {
    let url: URL?
    @State private var image: UIImage?

    var body: some View {
        Group {
            if let image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                Rectangle().fill(Color.secondary.opacity(0.15))
            }
        }
        .task(id: url) {
            guard let url, let data = try? Data(contentsOf: url) else { return }
            image = UIImage(data: data)
        }
    }
}
