import SwiftUI
import AuthenticationServices
import CloudKit

struct LoginView: View {
    @EnvironmentObject var cloudKitService: CloudKitService
    @AppStorage("appleUserIdentifier") private var appleUserIdentifier: String = ""
    @AppStorage("displayName") private var displayName: String = ""

    @State private var isWorking = false
    @State private var shareToPresent: CKShare?
    @State private var showShareSheet = false

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "map.fill")
                .font(.system(size: 64))
                .foregroundStyle(.tint)
            Text("足迹相册")
                .font(.largeTitle.bold())

            if appleUserIdentifier.isEmpty {
                SignInWithAppleButton(.signIn) { request in
                    request.requestedScopes = [.fullName]
                } onCompletion: { result in
                    handleSignIn(result)
                }
                .signInWithAppleButtonStyle(.black)
                .frame(height: 50)
                .padding(.horizontal, 40)
            } else if cloudKitService.accountStatus != .available {
                VStack(spacing: 8) {
                    ProgressView()
                    Text("请先在系统设置里登录 iCloud 账号")
                        .foregroundStyle(.secondary)
                }
            } else if !cloudKitService.isSharedZoneReady {
                VStack(spacing: 16) {
                    Text("还没有共享相册")
                        .font(.headline)
                    Button {
                        Task { await createAndShareAlbum() }
                    } label: {
                        if isWorking {
                            ProgressView()
                        } else {
                            Text("创建共享相册并邀请TA")
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isWorking)

                    Text("如果对方已经建好相册并把邀请链接发给你，直接打开那个链接接受邀请，回到这个 App 就会自动进入相册。")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 32)

                    if let errorMessage = cloudKitService.errorMessage {
                        Text(errorMessage)
                            .font(.footnote)
                            .foregroundStyle(.red)
                    }
                }
            } else {
                ProgressView()
            }
        }
        .padding()
        .task {
            await cloudKitService.refreshAccountStatus()
            if cloudKitService.accountStatus == .available {
                await cloudKitService.locateAlbum()
            }
        }
        .sheet(isPresented: $showShareSheet) {
            if let share = shareToPresent {
                CloudSharingView(share: share, container: CKContainer(identifier: CloudKitService.containerIdentifier))
            }
        }
    }

    private func handleSignIn(_ result: Result<ASAuthorization, Error>) {
        switch result {
        case .success(let authorization):
            guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential else { return }
            appleUserIdentifier = credential.user
            if let fullName = credential.fullName {
                let name = PersonNameComponentsFormatter().string(from: fullName)
                if !name.isEmpty { displayName = name }
            }
            if displayName.isEmpty { displayName = "我" }
        case .failure(let error):
            cloudKitService.errorMessage = error.localizedDescription
        }
    }

    private func createAndShareAlbum() async {
        isWorking = true
        defer { isWorking = false }
        await cloudKitService.createSharedAlbum()
        if let share = await cloudKitService.makeShare() {
            shareToPresent = share
            showShareSheet = true
        }
    }
}
