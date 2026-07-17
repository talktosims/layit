import SwiftUI

struct ContentView: View {
    var body: some View {
        WebAppView()
            .ignoresSafeArea(.container, edges: [.bottom, .horizontal])
            .background(Color(red: 0.031, green: 0.043, blue: 0.071))
    }
}
