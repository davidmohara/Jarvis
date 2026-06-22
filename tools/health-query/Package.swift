// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "HealthQuery",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "HealthQuery",
            path: "Sources/HealthQuery"
        )
    ]
)
