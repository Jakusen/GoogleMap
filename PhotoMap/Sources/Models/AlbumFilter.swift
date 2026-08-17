import Foundation

enum AlbumFilter: String, CaseIterable, Identifiable {
    case all = "全部"
    case mine = "我的"
    case partner = "TA的"

    var id: String { rawValue }
}
