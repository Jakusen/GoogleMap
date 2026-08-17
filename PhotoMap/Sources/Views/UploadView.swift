import SwiftUI
import PhotosUI
import CoreLocation

struct UploadView: View {
    @EnvironmentObject var cloudKitService: CloudKitService
    @StateObject private var locationService = LocationService()
    @AppStorage("displayName") private var displayName: String = "我"

    @State private var pickerItem: PhotosPickerItem?
    @State private var selectedImage: UIImage?
    @State private var showCamera = false
    @State private var isUploading = false
    @State private var statusMessage: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                if let selectedImage {
                    Image(uiImage: selectedImage)
                        .resizable()
                        .scaledToFit()
                        .frame(maxHeight: 320)
                        .cornerRadius(12)
                } else {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.secondary.opacity(0.15))
                        .frame(height: 320)
                        .overlay(Text("还没有选择照片").foregroundStyle(.secondary))
                }

                HStack(spacing: 16) {
                    PhotosPicker(selection: $pickerItem, matching: .images) {
                        Label("从相册选择", systemImage: "photo.on.rectangle")
                    }
                    .buttonStyle(.bordered)

                    Button {
                        showCamera = true
                    } label: {
                        Label("拍照", systemImage: "camera")
                    }
                    .buttonStyle(.bordered)
                }

                if let location = locationService.currentLocation {
                    Text("当前位置：\(location.coordinate.latitude, specifier: "%.5f")，\(location.coordinate.longitude, specifier: "%.5f")")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                } else {
                    Text("正在获取位置…")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Button {
                    Task { await upload() }
                } label: {
                    if isUploading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("上传")
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(selectedImage == nil || locationService.currentLocation == nil || isUploading)

                if let statusMessage {
                    Text(statusMessage)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Spacer()
            }
            .padding()
            .navigationTitle("上传照片")
            .onAppear {
                locationService.requestPermission()
                locationService.requestOneShotLocation()
            }
            .onChange(of: pickerItem) { _, newItem in
                Task {
                    if let data = try? await newItem?.loadTransferable(type: Data.self),
                       let image = UIImage(data: data) {
                        selectedImage = image
                    }
                }
            }
            .sheet(isPresented: $showCamera) {
                CameraCaptureView(image: $selectedImage)
            }
        }
    }

    private func upload() async {
        guard let image = selectedImage, let location = locationService.currentLocation else { return }
        isUploading = true
        statusMessage = nil

        await cloudKitService.uploadPhoto(
            image: image,
            coordinate: location.coordinate,
            timestamp: Date(),
            ownerName: displayName
        )

        isUploading = false
        if let error = cloudKitService.errorMessage {
            statusMessage = "上传失败：\(error)"
        } else {
            statusMessage = "上传成功"
            selectedImage = nil
            pickerItem = nil
        }
    }
}
