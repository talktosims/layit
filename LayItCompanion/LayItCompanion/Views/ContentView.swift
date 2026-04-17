// ContentView.swift
// Main app view: Paint Calc web app with native LiDAR scanning overlay

import SwiftUI
import ARKit
import WebKit

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var showScanner = false
    @State private var showLastScan = false
    @State private var webView: WKWebView?

    var body: some View {
        ZStack {
            // The paint calculator web app fills the screen
            WebAppView(appState: appState, onScanRequested: {
                showScanner = true
            }, onViewLastScan: {
                if appState.lastScannedRoom != nil {
                    showLastScan = true
                }
            })
            .ignoresSafeArea(edges: .bottom)
            .onAppear {
                // Grab webView reference after a brief delay for setup
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    // Find the WKWebView in the view hierarchy
                    if let window = UIApplication.shared.connectedScenes
                        .compactMap({ $0 as? UIWindowScene })
                        .flatMap({ $0.windows })
                        .first(where: { $0.isKeyWindow }),
                       let wv = findWebView(in: window) {
                        webView = wv
                    }
                }
            }
        }
        .sheet(isPresented: $showScanner) {
            NavigationStack {
                RoomScanView()
                    .environmentObject(appState)
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .cancellationAction) {
                            Button("Cancel") { showScanner = false }
                                .foregroundColor(.orange)
                        }
                    }
            }
            .onDisappear {
                // When scanner closes, if we have a scanned room, push it to the web app
                if let room = appState.scannedRoom {
                    appState.lastScannedRoom = room
                    WebAppView.pushScanToWebView(webView, room: room)
                    // Clear so it doesn't re-send on next dismiss
                    appState.scannedRoom = nil
                }
            }
        }
        .sheet(isPresented: $showLastScan) {
            if let room = appState.lastScannedRoom {
                NavigationStack {
                    RoomResultView(room: room, onConfirm: {
                        showLastScan = false
                    }, onRescan: {
                        showLastScan = false
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            showScanner = true
                        }
                    }, reviewOnly: true)
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .cancellationAction) {
                            Button("Close") { showLastScan = false }
                                .foregroundColor(.orange)
                        }
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    // Walk the view hierarchy to find the WKWebView
    private func findWebView(in view: UIView) -> WKWebView? {
        if let wv = view as? WKWebView { return wv }
        for subview in view.subviews {
            if let found = findWebView(in: subview) { return found }
        }
        return nil
    }
}

// Check if device supports RoomPlan
enum RoomPlanSupported {
    static var isSupported: Bool {
        if #available(iOS 16.0, *) {
            return ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh)
        }
        return false
    }
}
