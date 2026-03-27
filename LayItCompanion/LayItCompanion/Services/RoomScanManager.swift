// RoomScanManager.swift
// Manages RoomPlan capture session and converts results to paint calc format

import Foundation
import RoomPlan
import simd
import Combine
import AVFoundation

class RoomScanManager: NSObject, ObservableObject {
    @Published var isScanning = false
    @Published var scannedRoom: ScannedRoom?
    @Published var showError = false
    @Published var errorMessage = ""

    private(set) var captureSession: RoomCaptureSession!
    private var capturedRoom: CapturedRoom?

    override init() {
        super.init()
    }

    /// Called by the view representable to hand over the view's own capture session
    func setCaptureSession(_ session: RoomCaptureSession) {
        captureSession = session
        captureSession.delegate = self
        onSessionReady()
    }

    func startScanning() {
        scannedRoom = nil
        capturedRoom = nil

        // Request camera permission first
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        switch status {
        case .authorized:
            beginScan()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                DispatchQueue.main.async {
                    if granted {
                        self?.beginScan()
                    } else {
                        self?.showError = true
                        self?.errorMessage = "Camera access is required for room scanning. Please enable it in Settings > Paint Calc > Camera."
                    }
                }
            }
        default:
            showError = true
            errorMessage = "Camera access is required for room scanning. Please enable it in Settings > Paint Calc > Camera."
        }
    }

    private func beginScan() {
        isScanning = true

        // The capture session is set by the view representable after the view appears.
        // If already available, start immediately; otherwise it starts via onSessionReady().
        if captureSession != nil {
            let config = RoomCaptureSession.Configuration()
            captureSession.run(configuration: config)
        }
    }

    /// Called after setCaptureSession if scanning was already requested
    func onSessionReady() {
        if isScanning, captureSession != nil {
            let config = RoomCaptureSession.Configuration()
            captureSession.run(configuration: config)
        }
    }

    func stopScanning() {
        isScanning = false
        captureSession?.stop()
    }

    // Convert RoomPlan CapturedRoom to paint-calc-ready ScannedRoom
    private func convertToScannedRoom(room: CapturedRoom) -> ScannedRoom? {
        let walls = room.walls
        guard walls.count >= 3 else {
            showError = true
            errorMessage = "Not enough walls detected (\(walls.count)). Try scanning again and make sure all walls are visible."
            return nil
        }

        let metersToInches: Double = 39.3701

        // ── Extract wall segments with length AND height ──
        var wallSegments: [WallSegment] = []
        var wallHeights: [Double] = []

        struct WallEndpoints {
            var start: SIMD2<Float>
            var end: SIMD2<Float>
            var length: Float
            var height: Float
        }

        var wallEndpointsList: [WallEndpoints] = []

        for wall in walls {
            let center = wall.transform.columns.3
            let halfWidth = wall.dimensions.x / 2
            let wallHeight = wall.dimensions.y

            let localX = SIMD2<Float>(wall.transform.columns.0.x, wall.transform.columns.0.z)
            let localXNorm = normalize(localX)

            let centerXZ = SIMD2<Float>(center.x, center.z)
            let start = centerXZ - localXNorm * halfWidth
            let end = centerXZ + localXNorm * halfWidth

            let lengthInches = Double(wall.dimensions.x) * metersToInches
            let heightInches = Double(wallHeight) * metersToInches

            wallSegments.append(WallSegment(length: lengthInches, height: heightInches))
            wallHeights.append(heightInches)
            wallEndpointsList.append(WallEndpoints(start: start, end: end, length: wall.dimensions.x, height: wallHeight))
        }

        // ── Order wall endpoints to form closed polygon ──
        var ordered: [WallEndpoints] = []
        var remaining = wallEndpointsList
        ordered.append(remaining.removeFirst())

        while !remaining.isEmpty {
            let currentEnd = ordered.last!.end
            var bestIdx = 0
            var bestDist: Float = .infinity

            for i in 0..<remaining.count {
                let d1 = distance(currentEnd, remaining[i].start)
                let d2 = distance(currentEnd, remaining[i].end)

                if d1 < bestDist {
                    bestDist = d1
                    bestIdx = i
                }
                if d2 < bestDist {
                    bestDist = d2
                    bestIdx = i
                    remaining[i] = WallEndpoints(
                        start: remaining[i].end,
                        end: remaining[i].start,
                        length: remaining[i].length,
                        height: remaining[i].height
                    )
                }
            }

            ordered.append(remaining.remove(at: bestIdx))
        }

        // ── Build polygon from ordered endpoints ──
        var polygon: [RoomPoint] = []
        for seg in ordered {
            polygon.append(RoomPoint(
                x: Double(seg.start.x) * metersToInches,
                y: Double(seg.start.y) * metersToInches
            ))
        }

        // Normalize: shift so minimum corner is at origin
        let minX = polygon.map(\.x).min() ?? 0
        let minY = polygon.map(\.y).min() ?? 0
        polygon = polygon.map { RoomPoint(x: $0.x - minX, y: $0.y - minY) }

        // Bounding box
        let bbWidth = polygon.map(\.x).max() ?? 0
        let bbHeight = polygon.map(\.y).max() ?? 0

        // Floor/ceiling area from polygon
        let floorArea = ScannedRoom.calculateArea(polygon: polygon)

        // ── Average wall height ──
        let avgHeight = wallHeights.isEmpty ? 96.0 : wallHeights.reduce(0, +) / Double(wallHeights.count)

        // ── Rectangularity detection ──
        let isRect = detectRectangular(polygon: polygon, wallCount: walls.count)

        // ── Room length/width for quick mode ──
        var roomLength: Double = bbWidth
        var roomWidth: Double = bbHeight

        if isRect && wallSegments.count == 4 {
            // Sort walls by length, pair them
            let sorted = wallSegments.sorted { $0.length > $1.length }
            roomLength = (sorted[0].length + sorted[1].length) / 2
            roomWidth = (sorted[2].length + sorted[3].length) / 2
        }

        // ── Doors and windows ──
        let doors = room.doors
        let windows = room.windows

        let doorDims: [SurfaceDimension] = doors.map {
            SurfaceDimension(
                width: Double($0.dimensions.x) * metersToInches,
                height: Double($0.dimensions.y) * metersToInches
            )
        }

        let windowDims: [SurfaceDimension] = windows.map {
            SurfaceDimension(
                width: Double($0.dimensions.x) * metersToInches,
                height: Double($0.dimensions.y) * metersToInches
            )
        }

        return ScannedRoom(
            polygon: polygon,
            width: bbWidth,
            height: bbHeight,
            areaSqInches: floorArea,
            wallCount: polygon.count,
            scanDate: Date(),
            wallSegments: wallSegments,
            roomHeight: avgHeight,
            roomLength: roomLength,
            roomWidth: roomWidth,
            ceilingArea: floorArea,
            doorCount: doors.count,
            windowCount: windows.count,
            doorDimensions: doorDims,
            windowDimensions: windowDims,
            isRectangular: isRect
        )
    }

    /// Detect if the polygon is roughly rectangular:
    /// - Exactly 4 walls
    /// - All corner angles within 15 degrees of 90
    private func detectRectangular(polygon: [RoomPoint], wallCount: Int) -> Bool {
        guard wallCount == 4, polygon.count == 4 else { return false }

        let tolerance = 15.0 * .pi / 180.0  // 15 degrees in radians

        for i in 0..<polygon.count {
            let prev = polygon[(i + polygon.count - 1) % polygon.count]
            let curr = polygon[i]
            let next = polygon[(i + 1) % polygon.count]

            let v1 = (prev.x - curr.x, prev.y - curr.y)
            let v2 = (next.x - curr.x, next.y - curr.y)

            let dot = v1.0 * v2.0 + v1.1 * v2.1
            let mag1 = sqrt(v1.0 * v1.0 + v1.1 * v1.1)
            let mag2 = sqrt(v2.0 * v2.0 + v2.1 * v2.1)

            guard mag1 > 0.01 && mag2 > 0.01 else { return false }

            let cosAngle = dot / (mag1 * mag2)
            let angle = acos(min(1, max(-1, cosAngle)))

            // Check if angle is within tolerance of 90 degrees
            if abs(angle - .pi / 2) > tolerance {
                return false
            }
        }

        return true
    }
}

// MARK: - RoomCaptureSession Delegate
extension RoomScanManager: RoomCaptureSessionDelegate {
    func captureSession(_ session: RoomCaptureSession, didUpdate room: CapturedRoom) {
        // Live updates during scanning (could update a preview)
    }

    func captureSession(_ session: RoomCaptureSession, didEndWith data: CapturedRoomData, error: Error?) {
        DispatchQueue.main.async { [weak self] in
            self?.isScanning = false

            if let error = error {
                self?.showError = true
                self?.errorMessage = "Scan failed: \(error.localizedDescription)"
                return
            }

            // Process the final room data
            let builder = RoomBuilder(options: [.beautifyObjects])
            Task {
                do {
                    let finalRoom = try await builder.capturedRoom(from: data)
                    await MainActor.run {
                        self?.capturedRoom = finalRoom
                        self?.scannedRoom = self?.convertToScannedRoom(room: finalRoom)
                    }
                } catch {
                    await MainActor.run {
                        self?.showError = true
                        self?.errorMessage = "Processing failed: \(error.localizedDescription)"
                    }
                }
            }
        }
    }
}
