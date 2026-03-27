// PaintCalcCompanion
// LiDAR room scanner for the Paint Calc estimator app

import SwiftUI

@main
struct LayItCompanionApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .preferredColorScheme(.dark)
        }
    }
}
