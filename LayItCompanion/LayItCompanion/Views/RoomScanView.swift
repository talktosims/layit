// RoomScanView.swift
// RoomPlan-powered room scanning with live preview

import SwiftUI
import RoomPlan

// MARK: - RoomPlan UIView Wrapper
struct RoomCaptureViewRepresentable: UIViewRepresentable {
    let scanManager: RoomScanManager

    func makeUIView(context: Context) -> RoomCaptureView {
        let view = RoomCaptureView(frame: .zero)
        view.delegate = context.coordinator
        // Give the manager the view's own capture session
        scanManager.setCaptureSession(view.captureSession)
        return view
    }

    func updateUIView(_ uiView: RoomCaptureView, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator() }

    @objc(PaintCalcRoomCaptureCoordinator)
    class Coordinator: NSObject, RoomCaptureViewDelegate, NSCoding {
        override init() { super.init() }

        required init?(coder: NSCoder) { super.init() }

        func encode(with coder: NSCoder) {}

        func captureView(shouldPresent roomDataForProcessing: CapturedRoomData, error: Error?) -> Bool {
            return true
        }
        func captureView(didPresent processedResult: CapturedRoom, error: Error?) {}
    }
}

// MARK: - Scan View
struct RoomScanView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) var dismiss

    @StateObject private var scanManager = RoomScanManager()
    @State private var showResult = false

    private let gold = Color(red: 0.83, green: 0.66, blue: 0.26) // #d4a843

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            if scanManager.isScanning {
                // Live scan view
                RoomCaptureViewRepresentable(scanManager: scanManager)
                    .ignoresSafeArea()

                // Overlay controls
                VStack {
                    // Status indicator at top
                    HStack {
                        Circle()
                            .fill(Color.red)
                            .frame(width: 8, height: 8)

                        Text("Scanning")
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(.white)
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial)
                    .clipShape(Capsule())
                    .padding(.top, 8)

                    Spacer()

                    // Compact done button at bottom
                    Button(action: { scanManager.stopScanning() }) {
                        Text("Done")
                            .font(.system(size: 14, weight: .bold, design: .monospaced))
                            .foregroundColor(Color(white: 0.1))
                            .padding(.horizontal, 32)
                            .padding(.vertical, 12)
                            .background(gold)
                            .clipShape(Capsule())
                    }
                    .padding(.bottom, 40)
                }
            } else if let room = scanManager.scannedRoom {
                // Show result
                RoomResultView(room: room, onConfirm: {
                    appState.scannedRoom = room
                    appState.pushPaintScanToSync()
                    dismiss()
                }, onRescan: {
                    scanManager.startScanning()
                })
            } else {
                // Pre-scan instructions
                VStack(spacing: 24) {
                    Spacer()

                    Image(systemName: "camera.viewfinder")
                        .font(.system(size: 64))
                        .foregroundColor(gold)

                    Text("Scan Your Room")
                        .font(.system(size: 28, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)

                    VStack(alignment: .leading, spacing: 12) {
                        instructionRow(num: 1, text: "Point your camera at the floor")
                        instructionRow(num: 2, text: "Walk slowly around the room perimeter")
                        instructionRow(num: 3, text: "Keep walls, doors & windows in view")
                        instructionRow(num: 4, text: "Tap \"Done\" when you've gone all the way around")
                    }
                    .padding(.horizontal, 32)

                    Text("LiDAR will detect walls, doors, and windows automatically")
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundColor(.white.opacity(0.4))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 32)

                    Spacer()

                    Button(action: { scanManager.startScanning() }) {
                        HStack {
                            Image(systemName: "record.circle")
                            Text("Start Scanning")
                        }
                        .font(.system(size: 16, weight: .semibold, design: .monospaced))
                        .foregroundColor(Color(white: 0.1))
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(gold)
                        .cornerRadius(14)
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 30)
                }
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .alert("Scanning Error", isPresented: $scanManager.showError) {
            Button("OK") {}
        } message: {
            Text(scanManager.errorMessage)
        }
    }

    private func instructionRow(num: Int, text: String) -> some View {
        HStack(spacing: 14) {
            Text("\(num)")
                .font(.system(size: 11, weight: .bold, design: .monospaced))
                .foregroundColor(Color(white: 0.1))
                .frame(width: 28, height: 28)
                .background(gold)
                .clipShape(Circle())

            Text(text)
                .font(.system(size: 14, design: .monospaced))
                .foregroundColor(.white.opacity(0.9))
        }
    }
}
