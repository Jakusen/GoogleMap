import SwiftUI

struct ContentView: View {
    @EnvironmentObject var cloudKitService: CloudKitService
    @AppStorage("appleUserIdentifier") private var appleUserIdentifier: String = ""

    var body: some View {
        if appleUserIdentifier.isEmpty || !cloudKitService.isSharedZoneReady {
            LoginView()
        } else {
            TabView {
                TimelineView()
                    .tabItem { Label("时间轴", systemImage: "clock") }
                MapPinsView()
                    .tabItem { Label("地图", systemImage: "map") }
                UploadView()
                    .tabItem { Label("上传", systemImage: "plus.circle") }
            }
        }
    }
}
