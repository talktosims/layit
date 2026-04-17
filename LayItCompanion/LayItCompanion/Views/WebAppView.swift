// WebAppView.swift
// WKWebView wrapper for the Paint Calc web app
// Provides JS bridge for native LiDAR scanning

import SwiftUI
import WebKit

struct WebAppView: UIViewRepresentable {
    let appState: AppState
    let onScanRequested: () -> Void
    var onViewLastScan: (() -> Void)? = nil

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()

        // Set up JS bridge
        let bridge = context.coordinator
        config.userContentController.add(bridge, name: "paintCalcNative")

        // Allow inline media playback
        config.allowsInlineMediaPlayback = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = bridge
        webView.scrollView.bounces = false
        webView.isOpaque = false
        webView.backgroundColor = .clear

        // Load bundled paint-calculator.html
        if let htmlURL = Bundle.main.url(forResource: "paint-calculator", withExtension: "html", subdirectory: "WebApp") {
            webView.loadFileURL(htmlURL, allowingReadAccessTo: htmlURL.deletingLastPathComponent())
        } else {
            // Fallback: load from localhost (dev mode)
            if let url = URL(string: "http://localhost:8081/paint-calculator.html") {
                webView.load(URLRequest(url: url))
            }
        }

        bridge.webView = webView
        bridge.onScanRequested = onScanRequested
        bridge.onViewLastScan = onViewLastScan
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    func makeCoordinator() -> WebViewBridge {
        WebViewBridge(appState: appState)
    }

    // Push scan result to the web app
    static func pushScanToWebView(_ webView: WKWebView?, room: ScannedRoom) {
        guard let webView = webView else { return }
        let payload = room.toPaintCalcJSON()
        guard let data = try? JSONSerialization.data(withJSONObject: payload),
              let json = String(data: data, encoding: .utf8) else { return }
        webView.evaluateJavaScript("window.onLidarScan && window.onLidarScan(\(json))")
    }
}

// MARK: - JavaScript Bridge
class WebViewBridge: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
    let appState: AppState
    weak var webView: WKWebView?
    var onScanRequested: (() -> Void)?
    var onViewLastScan: (() -> Void)?

    init(appState: AppState) {
        self.appState = appState
    }

    // Handle messages from JavaScript: window.webkit.messageHandlers.paintCalcNative.postMessage({...})
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any],
              let action = body["action"] as? String else { return }

        switch action {
        case "scanRoom":
            // Web app requesting a LiDAR room scan
            DispatchQueue.main.async { [weak self] in
                self?.onScanRequested?()
            }

        case "viewLastScan":
            // Show the last scan polygon for review
            DispatchQueue.main.async { [weak self] in
                self?.onViewLastScan?()
            }

        case "haptic":
            let style = body["style"] as? String ?? "medium"
            triggerHaptic(style: style)

        default:
            print("Unknown bridge action: \(action)")
        }
    }

    // Inject native mode flag after page loads, then re-render so Scan Room button appears
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        webView.evaluateJavaScript("""
            window.PAINTCALC_NATIVE = true;
            window.PAINTCALC_HAS_LIDAR = \(RoomPlanSupported.isSupported ? "true" : "false");
            console.log('Paint Calc native bridge active, LiDAR: \(RoomPlanSupported.isSupported)');
            if (typeof window._nativeRender === 'function') { window._nativeRender(); }
        """)
    }

    private func triggerHaptic(style: String) {
        switch style {
        case "light":
            UIImpactFeedbackGenerator(style: .light).impactOccurred()
        case "heavy":
            UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
        case "success":
            UINotificationFeedbackGenerator().notificationOccurred(.success)
        case "error":
            UINotificationFeedbackGenerator().notificationOccurred(.error)
        default:
            UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        }
    }
}
