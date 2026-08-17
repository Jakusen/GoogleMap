import SwiftUI
import MapKit

struct MapPinsView: View {
    @EnvironmentObject var cloudKitService: CloudKitService
    @AppStorage("displayName") private var displayName: String = "我"
    @State private var filter: AlbumFilter = .all
    @State private var selectedPhoto: PhotoPin?
    @State private var cameraPosition: MapCameraPosition = .automatic

    private var filteredPhotos: [PhotoPin] {
        cloudKitService.photos
            .filter(matchesFilter)
            .sorted { $0.timestamp < $1.timestamp }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("筛选", selection: $filter) {
                    ForEach(AlbumFilter.allCases) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)
                .padding()

                Map(position: $cameraPosition, selection: $selectedPhoto) {
                    ForEach(filteredPhotos) { photo in
                        Marker(photo.ownerName, coordinate: photo.coordinate)
                            .tag(photo)
                    }
                    if filteredPhotos.count > 1 {
                        MapPolyline(coordinates: filteredPhotos.map(\.coordinate))
                            .stroke(.blue, lineWidth: 3)
                    }
                }
                .sheet(item: $selectedPhoto) { photo in
                    PhotoDetailView(photo: photo)
                        .presentationDetents([.medium])
                }
            }
            .navigationTitle("地图")
            .task { await cloudKitService.fetchPhotos() }
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

private struct PhotoDetailView: View {
    let photo: PhotoPin

    var body: some View {
        VStack(spacing: 16) {
            AsyncPhotoThumbnail(url: photo.assetURL)
                .aspectRatio(contentMode: .fit)
                .cornerRadius(12)
            Text(photo.ownerName).font(.headline)
            Text(photo.timestamp.formatted(date: .abbreviated, time: .shortened))
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}
