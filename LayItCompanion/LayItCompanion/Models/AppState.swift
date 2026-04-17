// AppState.swift
// Global app state shared across views

import SwiftUI
import Combine

class AppState: ObservableObject {
    // Sync passphrase (matches paint calculator web app)
    @Published var passphrase: String = "" {
        didSet {
            UserDefaults.standard.set(passphrase, forKey: "paintcalc_passphrase")
            if !passphrase.isEmpty {
                syncService.connect(passphrase: passphrase)
            }
        }
    }

    // Last scanned room (cleared after sync)
    @Published var scannedRoom: ScannedRoom?

    // Persists after sync so user can review the polygon
    @Published var lastScannedRoom: ScannedRoom?

    // Connection status
    @Published var syncStatus: SyncStatus = .disconnected

    // Navigation
    @Published var showScanner: Bool = false

    let syncService = FirebaseSyncService()

    init() {
        // Restore saved passphrase
        if let saved = UserDefaults.standard.string(forKey: "paintcalc_passphrase"), !saved.isEmpty {
            self.passphrase = saved
            syncService.connect(passphrase: saved)
        }
    }

    func pushPaintScanToSync() {
        guard let room = scannedRoom, !passphrase.isEmpty else { return }
        syncStatus = .connecting
        syncService.pushPaintCalcRoom(room, passphrase: passphrase) { [weak self] success in
            DispatchQueue.main.async {
                self?.syncStatus = success ? .synced : .error
            }
        }
    }
}

enum SyncStatus {
    case disconnected, connecting, connected, synced, error
}
