# 足迹相册（PhotoMap）

两个人共用的 iOS 相册：拍照/上传时自动记录当时的位置和时间，在地图上以大头针 + 时间顺序动线的方式展示，也有时间轴视图；两人的照片共享同一个相册，互相可见。

## 技术栈

- SwiftUI（iOS 17+）
- CloudKit（存储 + 两人之间的实时同步，通过共享 Record Zone 实现）
- Sign in with Apple（登录，免费，跟 iCloud 账号天然绑定）
- MapKit（地图大头针 + 动线）
- CoreLocation（拍照时定位）

代码在本容器里只能编写，无法编译——本地没有 Xcode/macOS 工具链。需要在你自己的 Mac 上生成工程并运行。

## 首次搭建（在你的 Mac 上）

1. 安装 [XcodeGen](https://github.com/yonaskolb/XcodeGen)（用来从 `project.yml` 生成 `.xcodeproj`，避免手改工程文件出错）：
   ```bash
   brew install xcodegen
   ```

2. 生成 Xcode 工程：
   ```bash
   cd PhotoMap
   xcodegen generate
   open PhotoMap.xcodeproj
   ```

3. 在 Xcode 里：
   - 选中 PhotoMap target → Signing & Capabilities → 把 Team 改成你自己的 Apple Developer 账号
   - Bundle Identifier 目前是 `com.reizen.photomap`，如果这个 ID 已被别人占用，改成你自己的（比如 `com.你的域名.photomap`），同时把 `project.yml` 里 `PRODUCT_BUNDLE_IDENTIFIER` 和 `com.apple.developer.icloud-container-identifiers` 里的 `iCloud.com.reizen.photomap` 一起改掉，改完重新 `xcodegen generate`
   - 确认 Signing & Capabilities 里出现了 iCloud（勾了 CloudKit）、Push Notifications、Sign in with Apple 三个能力——这些是从 `project.yml` 的 entitlements 自动生成的，正常情况不用手动加

4. 去 [CloudKit Dashboard](https://icloud.developer.apple.com/dashboard/) 选中对应容器，在 Development 环境的 Schema 里确认（第一次真机跑起来、创建过一条记录后，`Photo` 这个 Record Type 会自动出现）：
   - 把 `timestamp`、`latitude`、`longitude` 字段都标记为 **Queryable** 和 **Sortable**（时间轴排序、地图动线排序都要用到），`ownerName` 标记为 **Queryable**
   - 这一步不做的话，查询会报 "field is not marked queryable/sortable" 的错误

5. 真机运行（CloudKit 在模拟器上体验有限，建议用真机测）：
   - 你（作为相册创建者）先运行 App，登录后点"创建共享相册并邀请TA"，会弹出系统分享面板，通过信息/AirDrop 把邀请链接发给你爱人
   - 你爱人在她的手机上打开这个链接（需要先把 App 装到她手机上，见下面"给两个人用"），系统会跳转到 App 里自动接受邀请，之后她也能看到、上传到同一个相册

## 给两个人用（不用上架 App Store）

两人固定使用，不需要上架。免费方案是用你自己的 Mac + 免费 Apple ID，通过 Xcode 直接装到两部手机上，但签名 7 天过期，需要定期重新连接电脑安装；更省心（但要 $99/年）的方式是加入 Apple Developer Program，用 TestFlight 内部测试，装一次以后可以远程推送更新，不用反复用数据线连接。

## 目录结构

```
PhotoMap/
  project.yml              XcodeGen 工程配置
  Sources/
    App/                    App 入口 + 根视图（登录态判断）
    Models/                 PhotoPin（CKRecord 包装）、AlbumFilter（全部/我的/TA的）
    Services/               CloudKitService（同步逻辑）、LocationService（定位）
    Views/                  登录、上传、时间轴、地图、分享邀请等界面
```

## 上架前需要补的东西（现在不用管）

- 隐私政策页面、Support URL——用你已有的域名 `reizen-co.com` 挂一个页面即可，不需要新服务器
- App Store 截图、描述等素材

以上这些只在你决定正式上架时才需要，日常两人使用不受影响。
