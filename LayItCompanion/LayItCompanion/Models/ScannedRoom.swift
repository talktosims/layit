// ScannedRoom.swift
// Data model for a scanned room — converts RoomPlan output to paint calc format

import Foundation

struct RoomPoint: Codable {
    var x: Double  // inches, X-axis (left-right)
    var y: Double  // inches, Y-axis (bottom-top, Y=0 at bottom)
}

struct WallSegment: Codable {
    var length: Double  // inches
    var height: Double  // inches
    var area: Double { length * height }  // sq inches
}

struct SurfaceDimension: Codable {
    var width: Double   // inches
    var height: Double  // inches
}

struct ScannedRoom: Codable {
    var polygon: [RoomPoint]         // Wall vertices in inches, origin at bottom-left
    var width: Double                // Bounding box width in inches
    var height: Double               // Bounding box height in inches
    var areaSqInches: Double         // Floor area via shoelace formula
    var wallCount: Int               // Number of wall segments
    var scanDate: Date

    // Paint calc fields
    var wallSegments: [WallSegment]  // Individual walls with length AND height
    var roomHeight: Double           // Average wall height (inches)
    var roomLength: Double           // Longest wall pair average (inches) — for quick mode
    var roomWidth: Double            // Shortest wall pair average (inches) — for quick mode
    var ceilingArea: Double          // Ceiling area in sq inches (= floor area)
    var doorCount: Int               // Number of doors detected by RoomPlan
    var windowCount: Int             // Number of windows detected by RoomPlan
    var doorDimensions: [SurfaceDimension]    // Individual door sizes
    var windowDimensions: [SurfaceDimension]  // Individual window sizes
    var isRectangular: Bool          // true = 4 walls with ~90 degree corners

    // Computed: area in square feet
    var areaSqFeet: Double {
        areaSqInches / 144.0
    }

    // Total wall area in sq feet (all walls combined)
    var totalWallSqFeet: Double {
        wallSegments.reduce(0.0) { $0 + $1.area } / 144.0
    }

    // Ceiling area in sq feet
    var ceilingSqFeet: Double {
        ceilingArea / 144.0
    }

    // Convert to JSON payload for Firebase → paint calculator
    func toPaintCalcJSON() -> [String: Any] {
        return [
            "roomLength": round(roomLength * 10) / 10,
            "roomWidth": round(roomWidth * 10) / 10,
            "roomHeight": round(roomHeight * 10) / 10,
            "doorCount": doorCount,
            "windowCount": windowCount,
            "wallSegments": wallSegments.map { [
                "length": round($0.length * 10) / 10,
                "height": round($0.height * 10) / 10
            ] },
            "doorDimensions": doorDimensions.map { [
                "width": round($0.width * 10) / 10,
                "height": round($0.height * 10) / 10
            ] },
            "windowDimensions": windowDimensions.map { [
                "width": round($0.width * 10) / 10,
                "height": round($0.height * 10) / 10
            ] },
            "ceilingArea": round(ceilingArea * 10) / 10,
            "isRectangular": isRectangular,
            "wallCount": wallCount,
            "polygon": polygon.map { ["x": round($0.x * 10) / 10, "y": round($0.y * 10) / 10] },
            "timestamp": ISO8601DateFormatter().string(from: scanDate),
            "source": "companion-lidar"
        ]
    }

    // Shoelace formula for polygon area
    static func calculateArea(polygon: [RoomPoint]) -> Double {
        guard polygon.count >= 3 else { return 0 }
        var area: Double = 0
        var j = polygon.count - 1
        for i in 0..<polygon.count {
            area += (polygon[j].x + polygon[i].x) * (polygon[j].y - polygon[i].y)
            j = i
        }
        return abs(area / 2.0)
    }
}
