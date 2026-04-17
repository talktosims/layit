// FirebaseSyncService.swift
// Syncs scanned room data to Firebase Realtime Database
// Uses SHA-256 hash to match the paint calculator's sync path

import Foundation
import CryptoKit

class FirebaseSyncService: ObservableObject {
    private let databaseURL = "https://paint-calc-sync-default-rtdb.firebaseio.com"
    private var currentHash: String?

    // SHA-256 hash matching the paint calculator's crypto.subtle.digest implementation
    static func sha256Hash(_ passphrase: String) -> String {
        let trimmed = passphrase.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let data = Data(trimmed.utf8)
        let hash = SHA256.hash(data: data)
        return hash.map { String(format: "%02x", $0) }.joined()
    }

    func connect(passphrase: String) {
        currentHash = FirebaseSyncService.sha256Hash(passphrase)
    }

    // Push scanned room to Firebase for the paint calculator to pick up
    // Path: sync/{sha256-hash}/paintScan
    func pushPaintCalcRoom(_ room: ScannedRoom, passphrase: String, completion: @escaping (Bool) -> Void) {
        let hash = FirebaseSyncService.sha256Hash(passphrase)
        let path = "sync/\(hash)/paintScan"
        let url = URL(string: "\(databaseURL)/\(path).json")!

        let payload = room.toPaintCalcJSON()

        guard let body = try? JSONSerialization.data(withJSONObject: payload) else {
            completion(false)
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.httpBody = body
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Firebase sync error: \(error.localizedDescription)")
                completion(false)
                return
            }
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                print("Paint calc scan synced to Firebase at path: \(path)")
                completion(true)
            } else {
                completion(false)
            }
        }.resume()
    }

    // Read current state from Firebase (to check if paint calc is connected)
    func checkConnection(passphrase: String, completion: @escaping (Bool) -> Void) {
        let hash = FirebaseSyncService.sha256Hash(passphrase)
        let url = URL(string: "\(databaseURL)/sync/\(hash)/jobs.json?shallow=true")!

        URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data, let str = String(data: data, encoding: .utf8), str != "null" {
                completion(true)
            } else {
                completion(false)
            }
        }.resume()
    }
}
