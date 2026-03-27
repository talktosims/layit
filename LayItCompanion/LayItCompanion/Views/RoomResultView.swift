// RoomResultView.swift
// Shows the scanned room with paint-relevant dimensions for user confirmation

import SwiftUI

struct RoomResultView: View {
    let room: ScannedRoom
    let onConfirm: () -> Void
    let onRescan: () -> Void
    var reviewOnly: Bool = false

    private let gold = Color(red: 0.83, green: 0.66, blue: 0.26) // #d4a843

    var body: some View {
        VStack(spacing: 20) {
            Text(reviewOnly ? "Last Scan" : "Verify Your Room")
                .font(.system(size: 24, weight: .bold, design: .monospaced))
                .foregroundColor(gold)

            Text(room.isRectangular ? "Rectangular room detected" : "Non-rectangular room (\(room.wallCount) walls)")
                .font(.system(size: 12, design: .monospaced))
                .foregroundColor(.white.opacity(0.6))

            // Polygon canvas
            PolygonView(polygon: room.polygon, width: room.width, height: room.height)
                .frame(height: 220)
                .background(Color(white: 0.08))
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(gold.opacity(0.3), lineWidth: 1)
                )
                .padding(.horizontal, 16)

            // Stats grid — room dimensions
            VStack(spacing: 6) {
                HStack(spacing: 6) {
                    statCard(label: "Length", value: formatInches(room.roomLength))
                    statCard(label: "Width", value: formatInches(room.roomWidth))
                    statCard(label: "Height", value: formatInches(room.roomHeight))
                }

                HStack(spacing: 6) {
                    statCard(label: "Wall SF", value: String(format: "%.0f", room.totalWallSqFeet))
                    statCard(label: "Ceiling", value: String(format: "%.0f ft\u{00B2}", room.ceilingSqFeet))
                }

                HStack(spacing: 6) {
                    statCard(label: "Doors", value: "\(room.doorCount)", highlight: room.doorCount > 0)
                    statCard(label: "Windows", value: "\(room.windowCount)", highlight: room.windowCount > 0)
                    statCard(label: "Walls", value: "\(room.wallCount)")
                }
            }
            .padding(.horizontal, 16)

            Spacer()

            // Action buttons
            VStack(spacing: 10) {
                if reviewOnly {
                    Button(action: onConfirm) {
                        Text("Close")
                            .font(.system(size: 15, weight: .semibold, design: .monospaced))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color(white: 0.2))
                            .cornerRadius(14)
                            .overlay(
                                RoundedRectangle(cornerRadius: 14)
                                    .stroke(gold.opacity(0.3), lineWidth: 1)
                            )
                    }
                } else {
                    Button(action: onConfirm) {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                            Text("Confirm & Sync to Paint Calc")
                        }
                        .font(.system(size: 15, weight: .semibold, design: .monospaced))
                        .foregroundColor(Color(white: 0.1))
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(gold)
                        .cornerRadius(14)
                    }
                }

                Button(action: onRescan) {
                    Text("Scan Again")
                        .font(.system(size: 13, design: .monospaced))
                        .foregroundColor(.white.opacity(0.7))
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 20)
        }
    }

    private func statCard(label: String, value: String, highlight: Bool = false) -> some View {
        VStack(spacing: 4) {
            Text(label.uppercased())
                .font(.system(size: 9, design: .monospaced))
                .foregroundColor(.white.opacity(0.5))
            Text(value)
                .font(.system(size: 18, weight: .bold, design: .monospaced))
                .foregroundColor(highlight ? gold : .white)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 10)
        .background(Color(white: 0.1))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(gold.opacity(0.15), lineWidth: 1)
        )
    }

    private func formatInches(_ inches: Double) -> String {
        let rounded = Int(inches.rounded())
        if rounded >= 12 {
            let ft = rounded / 12
            let rem = rounded % 12
            if rem == 0 { return "\(ft)'" }
            return "\(ft)' \(rem)\""
        }
        return "\(rounded)\""
    }
}

// MARK: - Polygon Drawing View
struct PolygonView: View {
    let polygon: [RoomPoint]
    let width: Double
    let height: Double

    private let gold = Color(red: 0.83, green: 0.66, blue: 0.26)

    var body: some View {
        Canvas { context, size in
            guard polygon.count >= 3 else { return }

            let padding: CGFloat = 40
            let drawW = size.width - padding * 2
            let drawH = size.height - padding * 2
            let scaleX = drawW / CGFloat(width)
            let scaleY = drawH / CGFloat(height)
            let scale = min(scaleX, scaleY)
            let offX = (size.width - CGFloat(width) * scale) / 2
            let offY = (size.height - CGFloat(height) * scale) / 2

            func tx(_ x: Double) -> CGFloat { offX + CGFloat(x) * scale }
            // Flip Y: polygon has Y=0 at bottom, canvas has Y=0 at top
            func ty(_ y: Double) -> CGFloat { size.height - offY - CGFloat(y) * scale }

            // Fill
            var path = Path()
            path.move(to: CGPoint(x: tx(polygon[0].x), y: ty(polygon[0].y)))
            for i in 1..<polygon.count {
                path.addLine(to: CGPoint(x: tx(polygon[i].x), y: ty(polygon[i].y)))
            }
            path.closeSubpath()

            context.fill(path, with: .color(gold.opacity(0.1)))
            context.stroke(path, with: .color(gold), lineWidth: 2.5)

            // Edge labels
            for i in 0..<polygon.count {
                let j = (i + 1) % polygon.count
                let dx = polygon[j].x - polygon[i].x
                let dy = polygon[j].y - polygon[i].y
                let edgeLen = sqrt(dx * dx + dy * dy)
                guard edgeLen > 0.5 else { continue }

                let mx = (polygon[i].x + polygon[j].x) / 2
                let my = (polygon[i].y + polygon[j].y) / 2
                let len = sqrt(dx * dx + dy * dy)
                let perpX = -dy / len * 14
                let perpY = dx / len * 14

                let label = formatInchesShort(edgeLen)
                context.draw(
                    Text(label).font(.system(size: 10, design: .monospaced)).foregroundColor(gold),
                    at: CGPoint(x: tx(mx) + CGFloat(perpX), y: ty(my) + CGFloat(perpY))
                )
            }

            // Corner dots
            for point in polygon {
                let dot = Path(ellipseIn: CGRect(
                    x: tx(point.x) - 3, y: ty(point.y) - 3,
                    width: 6, height: 6
                ))
                context.fill(dot, with: .color(.orange))
            }
        }
    }

    private func formatInchesShort(_ inches: Double) -> String {
        let rounded = Int(inches.rounded())
        if rounded >= 12 {
            let ft = rounded / 12
            let rem = rounded % 12
            if rem == 0 { return "\(ft)'" }
            return "\(ft)'\(rem)\""
        }
        return "\(rounded)\""
    }
}
